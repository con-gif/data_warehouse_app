from flask import Blueprint, request, jsonify, send_file, url_for
import pandas as pd
import os
import tempfile
import io
from utilities import clean_csv_content

format_bp = Blueprint('format_bp', __name__)

@format_bp.route('/format', methods=['POST'])
def format_data():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file provided"}), 400

    try:
        content = file.read().decode('utf-8')
        cleaned_content = clean_csv_content(content)
        csv_buffer = io.StringIO(cleaned_content)

        # Load into DataFrame
        df = pd.read_csv(csv_buffer)
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

        # Save the DataFrame to a temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        formatted_file_path = temp_file.name
        df.to_csv(formatted_file_path, index=False)

        # Provide a download link for the formatted file
        download_url = url_for('format_bp.download_file', file_path=formatted_file_path, _external=True)

        return jsonify({
            "message": "File formatted successfully",
            "download_url": download_url
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error processing the file: {str(e)}"}), 500

@format_bp.route('/download', methods=['GET'])
def download_file():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    return send_file(file_path, as_attachment=True, download_name="formatted_data.csv")
