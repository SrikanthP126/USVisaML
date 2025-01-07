import requests
import json
import base64
import getpass

# Step 1: Define server details
OLD_SERVER_IP = "your_old_server_ip_or_domain"  # Replace with old server's IP or domain
AUTH_ENDPOINT = f"https://{OLD_SERVER_IP}:8083/SecureSphere/api/v1/auth/session"
SCAN_DETAILS_ENDPOINT = f"https://{OLD_SERVER_IP}:8083/SecureSphere/api/v1/conf/assessment/scans"

# Step 2: Authenticate with the old server
USERNAME = input("Enter your username for the old server: ")
PASSWORD = getpass.getpass("Enter your password for the old server (input will be hidden): ")

credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

def authenticate():
    try:
        print("Authenticating with the old server...")
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

def fetch_scan_details(scan_name, cookies):
    try:
        print(f"Fetching details for scan: {scan_name}...")
        url = f"{SCAN_DETAILS_ENDPOINT}/{scan_name}"
        response = requests.get(url, headers=headers, cookies=cookies, verify=False)
        if response.status_code == 200:
            return response.json()  # Return the scan details as JSON
        else:
            print(f"Failed to fetch details for scan {scan_name}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching details for scan {scan_name}: {e}")
        return None

def main():
    # Step 3: Authenticate with the old server
    cookies = authenticate()
    if not cookies:
        print("Authentication failed. Exiting...")
        return

    # Step 4: Load scan names from scans.json
    try:
        with open("scans.json", "r") as file:
            scan_names = [name.strip() for name in json.load(file) if name.startswith("PNC")]
        print(f"Loaded {len(scan_names)} scan names starting with 'PNC'.")
    except Exception as e:
        print(f"Error reading scans.json file: {e}")
        return

    # Step 5: Fetch details for each scan and save to detailed_scans.json
    detailed_scans = []
    for scan_name in scan_names:
        scan_details = fetch_scan_details(scan_name, cookies)
        if scan_details:
            detailed_scans.append(scan_details)

    try:
        with open("detailed_scans.json", "w") as file:
            json.dump(detailed_scans, file, indent=4)
        print("Detailed scans saved to detailed_scans.json.")
    except Exception as e:
        print(f"Error saving detailed scans: {e}")

if __name__ == "__main__":
    main()
