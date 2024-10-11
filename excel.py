import os
import pandas as pd
import json
import openpyxl
import hashlib

# Convert Excel to A360 JSON
def exceltojson():
    src_dir = "/path/to/excel/files"  # Update this path to the location of your Excel files
    dest_dir = "/path/to/output/json"  # Update this path to the output location for .a360 files
    
    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for filename in os.listdir(src_dir):
        if filename is not None and filename.endswith(".xlsx"):
            excel_filename = os.path.join(src_dir, filename)
            print("Processing Excel file:", excel_filename)
            
            # Load the Excel file
            workbook = openpyxl.load_workbook(excel_filename)
            worksheet = workbook["Sheet1"]  # Assuming the sheet name is 'Sheet1', update if necessary
            
            # Prepare the list to store JSON data
            json_data = []
            
            # Read the Excel data into a DataFrame
            df = pd.read_excel(excel_filename)

            # Segregate by Cost Center
            cost_centers = df['Cost Center'].unique()
            
            for cost_center in cost_centers:
                df_cost_center = df[df['Cost Center'] == cost_center]

                # Create the record's unique hash (relation_id)
                relation_id = hashlib.md5(str(cost_center).encode()).hexdigest()

                # Create the 'create_record' entry
                create_record = {
                    "operation": "create_record",
                    "relation_id": relation_id,
                    "record_metadata": {
                        "cost_center": df_cost_center.iloc[0]['Cost Center'],
                        "record_code": df_cost_center.iloc[0]['record_code'],
                        "last_date_of_data": df_cost_center.iloc[0]['Last Date of Data'],
                        "business_classification": df_cost_center.iloc[0]['Business Classification'],
                        "date_range": df_cost_center.iloc[0]['Date Range'],
                        "major_description": df_cost_center.iloc[0]['Major Description'],
                    }
                }
                json_data.append(create_record)

                # Add 'upload_new_file' entries for each file
                for _, row in df_cost_center.iterrows():
                    upload_new_file = {
                        "operation": "upload_new_file",
                        "relation_id": relation_id,
                        "file_metadata": {
                            "file_name": row['file_name'],
                            "file_path": row['file_path'],
                            "record_code": row['record_code'],
                            "file_tag": "file"  # Default tag, can be updated as needed
                        }
                    }
                    json_data.append(upload_new_file)

                # Save each JSON file for the Cost Center
                output_filename = os.path.join(dest_dir, f"{cost_center}.a360")
                with open(output_filename, 'w') as json_file:
                    json.dump(json_data, json_file, indent=4)
            
            print(f"Created .a360 files for Cost Center: {cost_center}")

# Run the function
exceltojson()
