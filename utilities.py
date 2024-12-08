import pandas as pd
from extensions import get_mongo_connection
import csv
import io


def clean_csv_content(file_content):
    """
    Cleans malformed CSV content by normalizing quotes and commas.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    reader = csv.reader(io.StringIO(file_content), skipinitialspace=True)

    for row in reader:
        cleaned_row = []
        for cell in row:
            if isinstance(cell, str):
                cleaned_cell = cell.strip().strip('"')
            else:
                cleaned_cell = cell
            cleaned_row.append(cleaned_cell)
        writer.writerow(cleaned_row)

    return output.getvalue()

# ... keep other utilities as is ...



def format_excel(file_path, output_file_path):
    """
    Format an uploaded file and save it as an Excel file.
    """
    try:
        # Determine the file type
        if file_path.endswith('.csv'):
            print("Reading CSV file...")
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_path.endswith('.xlsx'):
            print("Reading Excel file...")
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError("Unsupported file format. Only CSV and XLSX files are supported.")

        print("Data preview:")
        print(df.head())

        # If all data is in one column (commas separating values), split it
        if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
            print("Splitting data in a single column...")
            df = df.iloc[:, 0].str.split(',', expand=True)

        # Rename columns to make them MongoDB-friendly
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

        # Save to output Excel file
        output_file_path = output_file_path.replace('.csv', '.xlsx')  # Ensure .xlsx extension
        df.to_excel(output_file_path, index=False, engine='openpyxl')
        print(f"Formatted data saved to {output_file_path}")

    except Exception as e:
        raise ValueError(f"Error while formatting the file: {str(e)}")


def compare_data(new_data_path, comparison_fields):
    """
    Compare new data with existing data in MongoDB.
    """
    try:
        # Load new data
        df = pd.read_excel(new_data_path, engine='openpyxl')
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

        # Connect to MongoDB
        db = get_mongo_connection()
        records_collection = db["records"]

        matched_records = []
        unmatched_records = []

        for _, record in df.iterrows():
            query = {field: record[field] for field in comparison_fields if field in record}
            if records_collection.find_one(query):
                matched_records.append(record.to_dict())
            else:
                unmatched_records.append(record.to_dict())

        matched_df = pd.DataFrame(matched_records)
        unmatched_df = pd.DataFrame(unmatched_records)

        return matched_df, unmatched_df

    except Exception as e:
        raise ValueError(f"Error during comparison: {str(e)}")


def screen_data(conditions):
    """
    Screen data from MongoDB based on conditions.
    """
    try:
        # Connect to MongoDB
        db = get_mongo_connection()
        records_collection = db["records"]

        # Build query
        query = {}
        for field, value in conditions.items():
            if '%' in value:
                query[field] = {"$regex": value.replace('%', '.*'), "$options": "i"}  # Case-insensitive regex
            else:
                query[field] = value

        # Fetch matching records
        matching_records = list(records_collection.find(query))

        # Convert to DataFrame
        df = pd.DataFrame(matching_records)

        # Drop MongoDB's internal `_id` field if it exists
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

        return df

    except Exception as e:
        raise ValueError(f"Error during screening: {str(e)}")
    

