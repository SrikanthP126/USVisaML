import os
import json
import pandas as pd
import uuid
from datetime import datetime

# Security Classification Mapping
classification_map = {
    "Confidential": "C",
    "Highly Confidential": "HC",
    "Internal": "I",
    "Public": "P"
}

# Function to get the security classification abbreviation
def get_security_classification(value):
    return classification_map.get(value, "Unknown")

# Function to format the submission date
def get_submission_date():
    return datetime.utcnow().isoformat() + 'Z'

# Check if the file has already been processed
def is_file_processed(file_name, processed_files):
    return file_name in processed_files

# Log the processed file
def log_processed_file(file_name, log_file_path):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{file_name}\n")

# Function to process Excel and convert to JSON using pandas
def process_excel_file(file_path, output_directory, log_file_path, records_per_file=100):
    # Read the log to check already processed files
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            processed_files = log_file.read().splitlines()
    else:
        processed_files = []

    if is_file_processed(file_path, processed_files):
        print(f"File {file_path} has already been processed. Skipping.")
        return

    # Load Excel file with pandas
    excel_data = pd.ExcelFile(file_path)

    for sheet_name in excel_data.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        current_records = []
        file_counter = 1

        # Iterate over the rows in the DataFrame starting from row 9 (index 8 in pandas)
        for index, row in df.iterrows():
            if index < 8:
                continue  # Skip the first 8 rows which contain metadata, not actual data

            relation_id = str(uuid.uuid4())

            record_metadata = {
                "record_class": row[2],  # Assuming column C9
                "publisher": df.iloc[0, 1],  # B1
                "region": df.iloc[3, 1],  # B4
                "recordDate": row[8],  # Date
                "provenance": df.iloc[0, 3],  # D1
                "security_classification": get_security_classification(df.iloc[3, 3]),  # D4
                "contributor": df.iloc[2, 3],  # D3
                "creator": df.iloc[1, 1],  # B2
                "description": row[4],  # Description from row
                "language": "eng",
                "title": row[5],  # Title from row
                "Date Range": row[6],  # Date Range
                "Major Description": row[7],  # Major Description
                "Minor Description": row[8],  # Minor Description
                "Reference 1": row[9],  # Reference 1
                "submission_date": get_submission_date()
            }

            file_metadata = {
                "publisher": df.iloc[0, 1],  # B1
                "source_folder_path": row[1],  # Source folder path
                "source_file_name": row[0],  # Source file name
                "dz_file_name": row[0],  # dz file name
                "file_tag": "zip"  # Assuming a default file tag
            }

            create_record = {
                "operation": "create_record",
                "relation_id": relation_id,
                "record_metadata": record_metadata
            }

            upload_new_file = {
                "operation": "upload_new_file",
                "relation_id": relation_id,
                "file_metadata": file_metadata
            }

            current_records.append(create_record)
            current_records.append(upload_new_file)

            if len(current_records) >= records_per_file * 2:
                output_file_path = os.path.join(output_directory, f'{sheet_name}_{file_counter}.a360')
                with open(output_file_path, 'w') as json_file:
                    for record in current_records:
                        json.dump(record, json_file, separators=(',', ':'), ensure_ascii=False)
                        json_file.write("\n")
                current_records = []
                file_counter += 1

        if current_records:
            output_file_path = os.path.join(output_directory, f'{sheet_name}_{file_counter}.a360')
            with open(output_file_path, 'w') as json_file:
                for record in current_records:
                    json.dump(record, json_file, separators=(',', ':'), ensure_ascii=False)
                    json_file.write("\n")
            current_records = []

    log_processed_file(file_path, log_file_path)
    print(f"Finished processing {file_path}")

# Main function to monitor directory and process files
def check_directory_for_new_files(excel_directory, output_directory, log_file_path, polling_interval=10):
    print(f"Watching directory: {excel_directory} for new Excel files...")
    while True:
        for file_name in os.listdir(excel_directory):
            file_path = os.path.join(excel_directory, file_name)
            if file_name.endswith(".xlsx"):
                print(f"Processing new file: {file_path}")
                process_excel_file(file_path, output_directory, log_file_path)
        time.sleep(polling_interval)

if __name__ == "__main__":
    excel_directory = "/path/to/excel_directory/"
    output_directory = "/path/to/output_directory/"
    log_file_path = "/path/to/processed_files.log"
    check_directory_for_new_files(excel_directory, output_directory, log_file_path)
