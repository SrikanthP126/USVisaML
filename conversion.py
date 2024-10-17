import pandas as pd
import json
import uuid
import os
from openpyxl import load_workbook
from datetime import datetime

# Load the Excel file
excel_file_path = 'path_to_your_excel_file.xlsx'  # Replace with the actual Excel file path
wb = load_workbook(excel_file_path, data_only=True)

# Directory where the output files will be stored
output_directory = '/path/to/output_folder'  # Replace with your desired directory path

# Ensure the output directory exists, if not, create it
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Function to get file extension and map to file_tag
def get_file_tag(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.doc':
        return 'word'
    elif ext == '.pdf':
        return 'pdf'
    elif ext == '.zip':
        return 'zip'
    else:
        return 'unknown'

# Function to format date in ISO-8601, handle partial dates like '2021-12'
def format_iso_date(excel_date):
    try:
        # Check if the value is a string like '2021-12'
        if isinstance(excel_date, str):
            # If the date is in 'YYYY-MM' format, append '-01' to make it 'YYYY-MM-DD'
            if len(excel_date) == 7:  # Example: '2021-12'
                excel_date += '-01'  # Default to the first day of the month
        return datetime.strptime(excel_date, "%Y-%m-%d").isoformat() + "-05:00"
    except (ValueError, TypeError):
        return None  # Skip the date if it's not in the correct format

# Update this line in the main code to use the modified function
record_date = format_iso_date(sheet['D9'].value)  # Now handles partial dates like '2021-12'

# Process each sheet in the workbook
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    # Constants from rows 1-8
    publisher = sheet['B1'].value
    region = sheet['B4'].value
    provenance = sheet['D1'].value
    entitlement_tag = sheet['D4'].value
    contributor = sheet['D3'].value
    creator = sheet['B2'].value
    language = 'eng'  # Constant as per ISO-639-2

    # Iterate over rows starting from row 9
    record_counter = 1
    file_counter = 1
    records_per_file = 100
    current_records = []

    for row in sheet.iter_rows(min_row=9, values_only=True):
        if row[0] is None:
            break  # Stop processing if the row is empty

        # Dynamic values from current row
        record_class = row[2]
        record_date = format_iso_date(row[8]) if row[8] else None
        description = row[4]
        date_range = row[6]
        major_description = row[7]
        minor_description = row[8]
        reference_1 = row[9]
        source_folder_path = row[1]
        source_file_name = row[0]
        dz_file_name = row[0]
        file_tag = get_file_tag(source_file_name)

        # Generate unique relation_id
        relation_id = str(uuid.uuid4())

        # Prepare record_metadata
        record_metadata = {
            "record_class": record_class,
            "publisher": publisher,
            "region": region,
            "recordDate": record_date,
            "provenance": provenance,
            "entitlement_tag": entitlement_tag,
            "contributor": contributor,
            "creator": creator,
            "description": description,
            "language": language,
            "title": source_file_name,
            "Date Range": date_range,
            "Major Description": major_description,
            "Minor Description": minor_description,
            "Reference 1": reference_1
        }

        # Prepare file_metadata
        file_metadata = {
            "publisher": publisher,
            "source_folder_path": source_folder_path,
            "source_file_name": source_file_name,
            "dz_file_name": dz_file_name,
            "file_tag": file_tag
        }

        # Add "create_record" entry
        current_records.append({
            "operation": "create_record",
            "relation_id": relation_id,
            "record_metadata": record_metadata
        })

        # Add "upload_new_file" entry
        current_records.append({
            "operation": "upload_new_file",
            "relation_id": relation_id,
            "file_metadata": file_metadata
        })

        # Split into multiple JSON files if record limit is reached
        if len(current_records) >= records_per_file * 2:
            output_file_path = os.path.join(output_directory, f'{sheet_name}_{file_counter}.a360')
            with open(output_file_path, 'w') as json_file:
                json.dump(current_records, json_file, indent=4)
            current_records = []  # Reset for the next set
            file_counter += 1

    # Write the remaining records to a file
    if current_records:
        output_file_path = os.path.join(output_directory, f'{sheet_name}_{file_counter}.a360')
        with open(output_file_path, 'w') as json_file:
            json.dump(current_records, json_file, indent=4)

print("JSON files created successfully.")
