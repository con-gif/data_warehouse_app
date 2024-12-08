from flask import Blueprint, request, jsonify
from extensions import get_mongo_connection
from bson.objectid import ObjectId

tag_bp = Blueprint('tag_bp', __name__)

@tag_bp.route('/tag', methods=['POST'])
def tag_record():
    data = request.get_json()
    record_id = data.get('record_id')
    tag = data.get('tag')
    remarks = data.get('remarks')

    if not record_id or not tag:
        return jsonify({"message": "Record ID and tag are required"}), 400

    # Convert string ID to ObjectId
    try:
        record_id = ObjectId(record_id)
    except:
        return jsonify({"message": "Invalid record_id"}), 400

    db = get_mongo_connection()
    records_collection = db["records"]

    update_result = records_collection.update_one(
        {"_id": record_id},
        {"$set": {"tag": tag, "remarks": remarks}}
    )

    if update_result.matched_count == 0:
        return jsonify({"message": "Record not found"}), 404

    return jsonify({"message": "Tag and remarks updated successfully"}), 200
