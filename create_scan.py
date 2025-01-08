import json
import requests

# Base URL of the server
NEW_SERVER_URL = "https://new-server-ip:8083/SecureSphere/api/v1"

# API Endpoints
AUTH_ENDPOINT = f"{NEW_SERVER_URL}/auth/session"
CREATE_SCAN_ENDPOINT = f"{NEW_SERVER_URL}/scans"

# Credentials
USERNAME = "your_username"
PASSWORD = "your_password"

def authenticate():
    """Authenticate with the server and get session cookies."""
    response = requests.post(
        AUTH_ENDPOINT,
        json={"username": USERNAME, "password": PASSWORD},
        verify=False  # Set to True if using valid SSL certificates
    )
    if response.status_code == 200:
        print("Authentication successful!")
        return response.cookies
    else:
        print(f"Authentication failed: {response.status_code}")
        exit()

def validate_json(scan_details):
    """Validate the sample.json against the required schema."""
    required_fields = ["name", "policy", "dbType", "apply-to", "scheduling"]
    for field in required_fields:
        if field not in scan_details:
            raise ValueError(f"Missing required field: {field}")
    print("Validation successful!")

def create_scan(scan_details, cookies):
    """Create a new scan on the server using the API."""
    response = requests.post(
        CREATE_SCAN_ENDPOINT,
        json=scan_details,
        cookies=cookies,
        headers={"Content-Type": "application/json"},
        verify=False  # Set to True if using valid SSL certificates
    )
    if response.status_code == 201:
        print(f"Scan '{scan_details['name']}' created successfully!")
    else:
        print(f"Failed to create scan: {response.status_code}, {response.text}")

def main():
    # Step 1: Authenticate
    cookies = authenticate()

    # Step 2: Load and validate JSON
    with open("sample.json", "r") as file:
        scan_details = json.load(file)
    validate_json(scan_details)

    # Step 3: Create Scan
    create_scan(scan_details, cookies)

if __name__ == "__main__":
    main()
