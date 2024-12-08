from flask import Blueprint, request, jsonify
from utilities import compare_data
import os
import tempfile

compare_bp = Blueprint('compare_bp', __name__)

@compare_bp.route('/compare', methods=['POST'])
def compare():
    # Get uploaded file
    file = request.files['file']
    fields = request.form.getlist('fields')  # Fields for comparison

    if not file or not fields:
        return jsonify({"message": "File and fields are required"}), 400

    # Save file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]).name
    file.save(temp_file)

    try:
        # Call the comparison function
        matched_df, unmatched_df = compare_data(temp_file, fields)

        # Save matched and unmatched data to files
        matched_file = 'matched_data.xlsx'
        unmatched_file = 'unmatched_data.xlsx'

        matched_df.to_excel(matched_file, index=False)
        unmatched_df.to_excel(unmatched_file, index=False)

        return jsonify({
            "message": "Comparison complete",
            "matched_file": matched_file,
            "unmatched_file": unmatched_file,
            "matched_records": len(matched_df),
            "unmatched_records": len(unmatched_df)
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        # Cleanup the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
