from flask import Blueprint, request, jsonify
from utilities import screen_data
import os
import tempfile

screening_bp = Blueprint('screening_bp', __name__)

@screening_bp.route('/screen', methods=['POST'])
def screen_records():
    """
    Endpoint to screen records based on conditions.
    """
    conditions = request.get_json()
    if not conditions:
        return jsonify({"message": "No conditions provided"}), 400

    try:
        # Filter records using the conditions
        filtered_data = screen_data(conditions)

        # Save results to a temporary file
        output_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
        filtered_data.to_excel(output_file_path, index=False)

        return jsonify({"message": "Data filtered successfully", "file_path": output_file_path}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
