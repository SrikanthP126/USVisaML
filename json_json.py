import pandas as pd
import json
import os

# Define the folder where the output JSON should be saved
output_folder = '/path/to/your/folder'  # Replace with your desired folder path

# Create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_path = '/home/pj72963/RRS_Excel/Copy of PNC RRS.xlsx'
sheet_name = 'Record Classes'

df = pd.read_excel(file_path, sheet_name=sheet_name)
df.columns = df.columns.str.strip()

# List of class names that include "China operations"
china_operations_classes = ['ACC205', 'ACC305', 'ADM165', 'AUD165', 'TAX125']

json_list = []

for index, row in df.iterrows():
    retention_period_value = row['Retention Period']

    # Skip rows that should be omitted
    if 'days' in str(retention_period_value).lower() or 'months' in str(retention_period_value).lower():
        continue  # Skip rows with 'days' or 'months'
    
    if retention_period_value == 'ACT':
        continue  # Skip rows where retention is exactly 'ACT'
    
    if any(china_class in row['Record Class Name'] for china_class in china_operations_classes):
        continue  # Skip rows where class name includes China operations

    # Handle specific retention periods for class codes
    if row['Record Class Code'] == 'CML200':
        retention_period = 6 * 365
    elif row['Record Class Code'] == 'EHS120':
        retention_period = 30 * 365
    elif row['Record Class Code'] == 'HRE200':
        retention_period = 60 * 365
    elif row['Record Class Code'] == 'INV250':
        retention_period = 75 * 365
    elif retention_period_value == 'ACT+29':
        retention_period = 29 * 365
    elif retention_period_value in ['IND', 'PERM', 'Life of Corporation']:
        retention_period = 99999
    elif retention_period_value == 'MAX3':
        retention_period = 3 * 365
    elif retention_period_value == 'Employee Termination + 30 years':
        retention_period = 30 * 365
    elif retention_period_value == 'LI6':
        retention_period = 6 * 365
    else:
        try:
            # Convert years to days for numeric values
            retention_period = int(retention_period_value) * 365
        except (ValueError, TypeError):
            retention_period = None  # Skip or set to None if it can't be converted

    # Default retention_trigger_field to "RecordDate" and set to "EventDate" for specific terms
    retention_trigger_field = "EventDate" if retention_period_value in ['IND', 'PERM', 'Life of Corporation'] else "RecordDate"

    # Replace NaN with empty string for JSON compatibility
    row = row.where(pd.notnull(row), '')

    record = {
        "record_class_code": row['Record Class Code'],
        "record_class_name": row['Record Class Name'],
        "record_class_description": row['Record Class Description'],
        "retention_period": retention_period,
        "retention_trigger_field": retention_trigger_field,
        "jurisdictional_exceptions": []
    }

    # Only include retention_type if it is explicitly specified as "YearEnd" in row data
    if 'retention_type' in row and row['retention_type'] == 'YearEnd':
        record["retention_type"] = "YearEnd"

    json_list.append(record)

json_output = json.dumps(json_list, indent=4)

# Save the JSON output into the folder
output_file_path = os.path.join(output_folder, 'output.json')
with open(output_file_path, 'w') as json_file:
    json_file.write(json_output)

print(f"Successfully converted RRS_Excel to {output_file_path}!")