def validate_metadata(self, sheet_name, row_count, metadata):
    """
    Validate that all required metadata fields are not None or null.
    Raise an error if any field is invalid.
    """
    for key, value in metadata.items():
        if value is None or value == "":
            self.logger.error(
                f"Missing value for '{key}' in sheet '{sheet_name}', row {row_count}."
            )
            raise ValueError(
                f"Sheet '{sheet_name}', Row {row_count}: Missing value for '{key}'."
            )


############################################################################################

def process_excel_file(self):
    self.logger.info(f"\n=== Starting to process Excel file: {self.input_file} ===\n")

    try:
        wb = load_workbook(self.input_file, data_only=True)
    except Exception as e:
        self.logger.error(f"Error loading workbook: {e}")
        sys.exit(1)

    metadata_sheets = [sheet for sheet in wb.sheetnames if sheet.startswith("Metadata")]
    if not metadata_sheets:
        self.logger.error("No metadata sheets found in the workbook!")
        sys.exit(1)

    self.logger.info(f"Found {len(metadata_sheets)} metadata sheet(s) to process\n")

    for sheet_name in metadata_sheets:
        self.logger.info(f"\nProcessing sheet: {sheet_name}")
        sheet = wb[sheet_name]

        row_count = 0
        for row in sheet.iter_rows(min_row=9, values_only=True):
            row_count += 1

            # Extract metadata fields
            record_date = row[3]
            publisher = sheet["B1"].value
            region = sheet["B4"].value
            record_class = sheet["C9"].value
            provenance = sheet["D1"].value
            security_classification = sheet["D3"].value

            # Create a metadata dictionary
            metadata = {
                "record_date": record_date,
                "publisher": publisher,
                "region": region,
                "record_class": record_class,
                "provenance": provenance,
                "security_classification": security_classification,
            }

            # Validate metadata
            try:
                self.validate_metadata(sheet_name, row_count, metadata)
            except ValueError as e:
                self.logger.error(str(e))
                print(f"Error: {str(e)}. Please fix the data and rerun.")
                sys.exit(1)

            # Continue processing...
            self.logger.info(f"Row {row_count}: All metadata is valid.")
