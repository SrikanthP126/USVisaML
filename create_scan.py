import requests
import json
import base64
import getpass

# Step 1: Define server details
NEW_SERVER_IP = "your_new_server_ip_or_domain"  # Replace with new server's IP or domain
AUTH_ENDPOINT = f"https://{NEW_SERVER_IP}:8083/SecureSphere/api/v1/auth/session"
CREATE_SCAN_ENDPOINT = f"https://{NEW_SERVER_IP}:8083/SecureSphere/api/v1/conf/assessment/scans"

# Step 2: Authenticate with the new server
def authenticate():
    username = input("Enter your username for the new server: ")
    password = getpass.getpass("Enter your password for the new server (input will be hidden): ")
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }

    try:
        print("Authenticating with the new server...")
        response = requests.post(AUTH_ENDPOINT, headers=headers, verify=False)
        if response.status_code == 200:
            print("Authentication successful!")
            return response.cookies  # Return session cookies for subsequent requests
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

# Step 3: Create scans using data from sample.json
def create_scan(scan_data, cookies):
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Creating scan: {scan_data.get('name')}...")
        response = requests.post(CREATE_SCAN_ENDPOINT, headers=headers, cookies=cookies, json=scan_data, verify=False)
        if response.status_code == 201:  # Assuming 201 is the success code for creation
            print(f"Scan created successfully: {scan_data.get('name')}")
            return True
        else:
            print(f"Failed to create scan {scan_data.get('name')}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error creating scan {scan_data.get('name')}: {e}")
        return False

# Step 4: Main function
def main():
    # Authenticate with the new server
    cookies = authenticate()
    if not cookies:
        print("Authentication failed. Exiting...")
        return

    # Load sample.json data
    try:
        with open("sample.json", "r") as file:
            scans_data = json.load(file)
            print(f"Loaded {len(scans_data)} scan entries from sample.json.")
    except Exception as e:
        print(f"Error reading sample.json file: {e}")
        return

    # Create scans
    for scan_data in scans_data:
        success = create_scan(scan_data, cookies)
        if not success:
            print(f"Skipping scan creation for {scan_data.get('name')} due to an error.")

    print("Scan creation process completed.")

if __name__ == "__main__":
    main()
