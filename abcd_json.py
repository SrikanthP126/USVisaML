import os
import json
import pandas as pd

# Load Excel file
input_file_path = '/path/to/your/input_excel_file.xlsx'  # Replace with your file path
output_directory = '/path/to/your/output_directory/'  # Replace with your output directory path

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Function to convert retention period to days
def convert_retention_period(retention_period):
    try:
        if retention_period in ["Life of Corporation", "IND", "LI"]:
            return 9999999
        elif retention_period == "MAX3":
            return 1095
        elif retention_period == "PERM":
            return 9999999
        else:
            # Split the period into number and unit, e.g., "6 years" -> "6", "years"
            parts = retention_period.split()
            if len(parts) == 2:
                number = int(parts[0])
                unit = parts[1].lower()
                if unit.startswith("year"):
                    return number * 365
                elif unit.startswith("month"):
                    return number * 30
            elif len(parts) == 1 and parts[0].isdigit():
                # If only a number is provided, assume years
                return int(parts[0]) * 365
    except ValueError:
        pass
    # If retention is in "days", "ACT", or cannot be parsed, return None
    return None

# Function to determine retention trigger field based on retention period
def get_retention_trigger_field(retention_period):
    if "year" in retention_period or "month" in retention_period:
        return "RecordDate"
    else:
        return "EventDate"

# Load data from Excel
df = pd.read_excel(input_file_path, sheet_name="Sheet1")  # Update sheet name if needed

# Filter out rows based on specified conditions
df = df[~df["Record Class Name"].str.contains("China Operations", na=False)]
df = df[~df["Retention Period"].str.contains("ACT", na=False)]
df = df[~df["Retention Period"].str.contains("day", case=False, na=False)]

# Initialize an empty list to store JSON records
records = []

for _, row in df.iterrows():
    retention_period = row["Retention Period"]
    retention_days = convert_retention_period(retention_period)
    
    # Skip row if retention_days could not be determined (e.g., ACT, days)
    if retention_days is None:
        continue
    
    # Prepare JSON record according to mappings and requirements
    record = {
        "record_class_code": row["Record Class Code"],
        "record_class_name": row["Record Class Name M Edit"],
        "record_class_description": row["Record Class Description M Edits"],
        "retention_period": retention_days,
        "retention_trigger_field": get_retention_trigger_field(retention_period),
        "retention_type": "YearEnd",
        "jurisdictional_exceptions": []
    }
    
    # Add record to the list
    records.append(record)

# Define output file path
output_file_path = os.path.join(output_directory, "output.json")

# Write JSON records to file
with open(output_file_path, 'w') as output_file:
    json.dump(records, output_file, indent=4)

# Sanity checks
print(f"Total records written: {len(records)}")
if any("days" in record["retention_period"] for record in records):
    print("Warning: Found records with 'days' in retention period.")
if any("ACT" in record["retention_period"] for record in records):
    print("Warning: Found records with 'ACT' in retention period.")
if any("China Operations" in record["record_class_name"] for record in records):
    print("Warning: Found records with 'China Operations' in the name.")
if not all(record["retention_type"] == "YearEnd" for record in records):
    print("Warning: Found records without 'YearEnd' as retention_type.")
if not all("jurisdictional_exceptions" in record for record in records):
    print("Warning: Found records missing 'jurisdictional_exceptions'.")
