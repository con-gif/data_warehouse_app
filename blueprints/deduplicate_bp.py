from flask import Blueprint, jsonify, request
from extensions import get_mongo_connection
from bson.objectid import ObjectId
import threading
import uuid

deduplicate_bp = Blueprint('deduplicate_bp', __name__)

JOB_STATUS = {}

def run_deduplication(job_id):
    db = get_mongo_connection()
    records_collection = db["records"]

    JOB_STATUS[job_id] = {"status": "running", "removed": 0}

    # Ensure index on 'phone' for performance: 
    # Run once elsewhere or ensure it's created before large dedupe:
    # db.records.create_index([("phone", 1)])

    total_removed = 0
    JOB_STATUS[job_id]["status"] = "running"

    current_phone = None
    current_ids = []

    # Use a cursor to stream through all documents sorted by phone.
    cursor = records_collection.find(
        {},  # no filter, process all docs
        {"phone": 1}  # only retrieve the phone field (and _id implicitly)
    ).sort("phone", 1)

    for doc in cursor:
        phone = doc.get("phone")

        if phone != current_phone:
            # We have reached a new phone number, handle duplicates for the old one
            if current_phone is not None and len(current_ids) > 1:
                # Remove duplicates for previous phone
                to_keep = current_ids[0]
                to_remove = current_ids[1:]
                delete_result = records_collection.delete_many({"_id": {"$in": to_remove}})
                removed = delete_result.deleted_count
                total_removed += removed
                JOB_STATUS[job_id]["removed"] = total_removed

            # Reset for the new phone
            current_phone = phone
            current_ids = []

        # Add this doc's _id to the current phone's list
        current_ids.append(doc["_id"])

    # After the loop ends, we must handle the last phone group
    if current_ids and len(current_ids) > 1:
        to_keep = current_ids[0]
        to_remove = current_ids[1:]
        delete_result = records_collection.delete_many({"_id": {"$in": to_remove}})
        removed = delete_result.deleted_count
        total_removed += removed
        JOB_STATUS[job_id]["removed"] = total_removed

    JOB_STATUS[job_id]["status"] = "completed"
    JOB_STATUS[job_id]["removed"] = total_removed


@deduplicate_bp.route('/deduplicate', methods=['POST'])
def deduplicate():
    job_id = str(uuid.uuid4())
    JOB_STATUS[job_id] = {"status": "starting", "removed": 0}
    thread = threading.Thread(target=run_deduplication, args=(job_id,))
    thread.start()

    return jsonify({"message": "Deduplication by phone started (streaming approach)", "job_id": job_id}), 202

@deduplicate_bp.route('/deduplicate/status', methods=['GET'])
def deduplicate_status():
    job_id = request.args.get("job_id")
    if not job_id or job_id not in JOB_STATUS:
        return jsonify({"message": "Invalid or missing job_id"}), 400

    status_info = JOB_STATUS[job_id]
    return jsonify({
        "status": status_info["status"],
        "duplicates_removed": status_info["removed"]
    }), 200
