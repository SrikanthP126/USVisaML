cost_center = sheet['B3'].value

# Convert cost_center to string even if it's in General format
if isinstance(cost_center, (int, float)):  # If it's a number, convert to string first
    cost_center = str(int(cost_center))  # Remove any decimals
elif isinstance(cost_center, str):  # If it's a string, strip any extra spaces
    cost_center = cost_center.strip()

# Ensure the cost_center is padded to 12 digits
if cost_center.isdigit():
    cost_center = cost_center.zfill(12)

print(f"Processed cost_center: {cost_center}")





# Assuming row[5] is the correct column for recordDate
record_date = row[5]  # Extract date from the correct column
formatted_record_date = format_iso_date(record_date)  # Format it using the helper function
print(f"Original record_date: {record_date}, Formatted record_date: {formatted_record_date}")





import calendar

def format_iso_date(excel_date):
    try:
        if isinstance(excel_date, str):
            if len(excel_date) == 7:  # Year-Month format (e.g., 2022-02)
                year, month = excel_date.split('-')
                last_day = calendar.monthrange(int(year), int(month))[1]  # Get last day of the month
                excel_date = f"{year}-{month}-{last_day}"  # Construct the full date
            return datetime.strptime(excel_date, "%Y-%m-%d").isoformat() + "-05:00"
    except (ValueError, TypeError):
        return None
