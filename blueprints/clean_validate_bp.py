from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import os
import tempfile
import io
from utilities import clean_csv_content

clean_validate_bp = Blueprint('clean_validate_bp', __name__)

@clean_validate_bp.route('/', methods=['POST'])
def clean_validate_csv():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file provided"}), 400

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.csv', '.txt', '.xlsx']:
        return jsonify({"message": "Unsupported file format. Please upload a CSV, TXT, or XLSX file."}), 400

    try:
        file_content = file.read().decode('utf-8')
        cleaned_content = clean_csv_content(file_content)

        csv_buffer = io.StringIO(cleaned_content)
        df = pd.read_csv(csv_buffer)

        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        df.dropna(how='all', inplace=True)
        df = df.where(pd.notnull(df), None)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        df.to_csv(temp_file.name, index=False)
        return send_file(temp_file.name, as_attachment=True, download_name="cleaned_file.csv")

    except Exception as e:
        return jsonify({"message": f"Error cleaning and validating file: {str(e)}"}), 500
