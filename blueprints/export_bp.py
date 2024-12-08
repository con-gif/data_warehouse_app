# blueprints/export_bp.py
from flask import Blueprint, request, jsonify, send_file
from os import path
import pandas as pd

# Create a Blueprint for export functionality
export_bp = Blueprint('export_bp', __name__)

# Define the directory where the data files are stored
DATA_DIR = path.abspath(path.join(path.dirname(__file__), '..'))  # Root directory of the app

@export_bp.route('/export', methods=['GET'])
def export_dataset():
    dataset = request.args.get('dataset')
    fields = request.args.get('fields', '*')

    # Validate dataset type
    filename_map = {
        'deduplicated': 'deduplicated_data.csv',
        'duplicate': 'duplicate_data.csv',
        'matched': 'matched_data.csv',
        'unmatched': 'unmatched_data.csv'
    }
    filename = filename_map.get(dataset)

    if not filename:
        return jsonify({"message": "Invalid dataset specified"}), 400

    # Construct the full path to the file
    full_path = path.join(DATA_DIR, filename)
    if not path.exists(full_path):
        return jsonify({"message": f"File not found: {filename}"}), 404

    try:
        # Load the dataset as a DataFrame
        df = pd.read_csv(full_path)

        # Filter columns if fields are specified
        if fields != '*':
            field_list = [field.strip() for field in fields.split(',')]
            df = df[field_list]

        # Save to a temporary CSV file to be downloaded
        output_filename = path.join(DATA_DIR, 'output_data.csv')
        df.to_csv(output_filename, index=False)

        # Send the file to the user
        return send_file(output_filename, as_attachment=True)
    except KeyError as e:
        return jsonify({"message": f"Invalid field(s) specified: {e}"}), 400
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
