import os
import json
import datetime
import uuid

# Security Classification Mapping
classification_map = {
    "Confidential": "C",
    "Highly Confidential": "HC",
    "Internal": "I",
    "Public": "P"
}

# Function to get the security classification abbreviation
def get_security_classification(value):
    return classification_map.get(value, "Unknown")  # Default to "Unknown" if not found

# Function to format the submission date
def get_submission_date():
    return datetime.datetime.utcnow().isoformat() + 'Z'  # ISO 8601 timestamp

# Function to process new Excel file and generate JSON
def process_excel_file(file_path, output_directory):
    # Assume we load data from the Excel file (replacing this with real Excel loading logic)
    excel_data = load_excel_file(file_path)

    for sheet_name, sheet in excel_data.items():
        current_records = []
        file_counter = 1

        # Iterate over the rows in the Excel sheet
        for row_index, row in enumerate(sheet):
            if row_index < 8:
                continue  # Skip the first 8 rows

            # Generate unique relation ID for each pair of create_record and upload_new_file
            relation_id = str(uuid.uuid4())

            # Map fields from Excel to JSON
            record_metadata = {
                "record_class": row[2],  # Assuming column C9
                "publisher": sheet['B1'],  # B1
                "region": sheet['B4'],  # B4
                "recordDate": row[8],  # Date
                "provenance": sheet['D1'],  # D1
                "security_classification": get_security_classification(sheet['D4']),  # D4
                "contributor": sheet['D3'],  # D3
                "creator": sheet['B2'],  # B2
                "description": row[4],  # Description
                "language": "eng",  # Hardcoded as per requirement
                "title": row[5],  # Title
                "Date Range": row[6],  # Date Range
                "Major Description": row[7],  # Major Description
                "Minor Description": row[8],  # Minor Description
                "Reference 1": row[9],  # Reference 1
                "submission_date": get_submission_date()
            }

            file_metadata = {
                "publisher": sheet['B1'],  # B1
                "source_folder_path": row[1],  # Source folder path
                "source_file_name": row[0],  # Source file name
                "dz_file_name": row[0],  # dz file name
                "file_tag": "zip"  # Assuming the file tag is "zip" based on extension
            }

            # Create JSON data
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

            # Append both operations to the current records
            current_records.append(create_record)
            current_records.append(upload_new_file)

        # Write out JSON files
        output_file_path = os.path.join(output_directory, f'{sheet_name}_output_{file_counter}.a360')
        with open(output_file_path, 'w') as json_file:
            for record in current_records:
                json.dump(record, json_file, separators=(',', ':'))
                json_file.write("\n")

        print(f"Processed and saved JSON for {file_path}")

# Function to load Excel data (stub for actual Excel loading logic)
def load_excel_file(file_path):
    # Replace with actual logic to read Excel
    return {
        "sheet1": [  # Fake data for demonstration purposes
            ["FileName1.zip", "FolderPath1", "Class1", "Description1", "DateRange1", "MajorDesc1", "MinorDesc1", "Ref1"],
            ["FileName2.zip", "FolderPath2", "Class2", "Description2", "DateRange2", "MajorDesc2", "MinorDesc2", "Ref2"],
        ]
    }

# Main code
if __name__ == "__main__":
    excel_directory = "/path/to/excel_directory"
    output_directory = "/path/to/output_directory"
    
    # Loop through files in the directory and process each Excel file
    for file_name in os.listdir(excel_directory):
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(excel_directory, file_name)
            process_excel_file(file_path, output_directory)
    
    print("All files processed.")
