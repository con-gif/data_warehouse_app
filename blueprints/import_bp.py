from flask import Blueprint, request, jsonify
import pandas as pd
from extensions import get_mongo_connection
from pymongo import InsertOne

import_bp = Blueprint('import_bp', __name__)

@import_bp.route('/import', methods=['POST'])
def import_data():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file provided"}), 400

    try:
        # Read file content into memory
        content = file.read().decode('utf-8', errors='replace').strip()
        lines = content.splitlines()

        if not lines:
            return jsonify({"message": "No data found in the file"}), 400

        # Parse CSV manually with optimized processing
        header = [h.strip().strip('"') for h in lines[0].split(',')]
        max_fields = len(header)

        records = []
        BATCH_SIZE = 10000
        db = get_mongo_connection()
        collection = db["records"]

        for line in lines[1:]:
            fields = [f.strip().strip('"') for f in line.split(',')]

            # Normalize row length
            if len(fields) < max_fields:
                fields += [None] * (max_fields - len(fields))
            elif len(fields) > max_fields:
                fields = fields[:max_fields]

            record = dict(zip(header, fields))
            records.append(record)

            # Insert in batches
            if len(records) >= BATCH_SIZE:
                collection.insert_many(records)
                records.clear()

        # Final insert for remaining records
        if records:
            collection.insert_many(records)

        return jsonify({
            "message": "Data imported successfully",
            "inserted_records": collection.estimated_document_count()
        }), 201

    except Exception as e:
        return jsonify({"message": f"Error processing the file: {str(e)}"}), 500
