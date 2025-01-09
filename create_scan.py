import requests
import json
import base64
import getpass



def authenticate():
    """Authenticate with the new server and return session cookies."""
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

def create_scan(scan_data, cookies):
    """Create a scan on the new server using the provided scan data."""
    headers = {
        "Content-Type": "application/json"
    }

    # Use scanName for the URL endpoint
    scan_name = scan_data.get("scanName").strip()
    url = f"{CREATE_SCAN_ENDPOINT}/{scan_name}"

    try:
        print(f"Creating scan: {scan_name}...")
        response = requests.post(url, headers=headers, cookies=cookies, json=scan_data, verify=False)
        if response.status_code == 201:  # Assuming 201 is the success code for creation
            print(f"Scan created successfully: {scan_name}")
            return True
        elif response.status_code == 400:
            print(f"Failed to create scan {scan_name}: {response.status_code} - Bad request. Please check your data.")
            return False
        elif response.status_code == 409:  # Conflict, possibly duplicate scan name
            print(f"Scan {scan_name} already exists: {response.status_code} - {response.text}")
            return False
        else:
            print(f"Failed to create scan {scan_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error creating scan {scan_name}: {e}")
        return False

def main():
    """Main function to create scans using data from sample.json."""
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

    # Validate loaded data format
    if not isinstance(scans_data, list):
        print("Error: sample.json must contain a list of dictionaries.")
        return

    # Create scans
    for scan_data in scans_data:
        if isinstance(scan_data, dict):  # Ensure the entry is a dictionary
            success = create_scan(scan_data, cookies)
            if not success:
                print(f"Skipping scan creation for {scan_data.get('scanName')} due to an error.")
        else:
            print(f"Skipping invalid scan entry: {scan_data}")

    print("Scan creation process completed.")

if __name__ == "__main__":
    main()
