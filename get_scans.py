import requests
import json
import base64
import getpass

# Step 1: Define server details
OLD_SERVER_IP = "your_old_server_ip_or_domain"  # Replace with old server's IP or domain
AUTH_ENDPOINT = f"https://{OLD_SERVER_IP}:8083/SecureSphere/api/v1/auth/session"
SCANS_ENDPOINT = f"https://{OLD_SERVER_IP}:8083/SecureSphere/api/v1/scans"

# Step 2: Authenticate with the old server
USERNAME = input("Enter your username for the old server: ")
PASSWORD = getpass.getpass("Enter your password for the old server (input will be hidden): ")

credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

# Step 3: Authenticate with the old server
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

# Step 4: Fetch all scans (basic information)
def fetch_all_scans(cookies):
    try:
        print("Fetching the list of scans...")
        response = requests.get(SCANS_ENDPOINT, headers=headers, cookies=cookies, verify=False)
        if response.status_code == 200:
            scans = response.json()
            print(f"Successfully retrieved {len(scans)} scans.")
            return scans
        else:
            print(f"Failed to fetch scans: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error during fetching scans: {e}")
        return []

# Step 5: Fetch detailed information for each scan
def fetch_scan_details(scans, cookies):
    detailed_scans = []
    for scan in scans:
        scan_id = scan["id"]  # Assuming "id" is the unique identifier for each scan
        scan_name = scan["name"]
        print(f"Fetching details for scan: {scan_name} (ID: {scan_id})...")
        scan_details_endpoint = f"{SCANS_ENDPOINT}/{scan_id}"
        try:
            response = requests.get(scan_details_endpoint, headers=headers, cookies=cookies, verify=False)
            if response.status_code == 200:
                detailed_scan = response.json()
                detailed_scans.append(detailed_scan)
            else:
                print(f"Failed to fetch details for scan {scan_name}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching details for scan {scan_name}: {e}")
    return detailed_scans

# Step 6: Save detailed scans to a JSON file
def save_detailed_scans(detailed_scans):
    try:
        with open("detailed_scans.json", "w") as file:
            json.dump(detailed_scans, file, indent=4)
        print("Detailed scans saved to detailed_scans.json.")
    except Exception as e:
        print(f"Error saving detailed scans: {e}")

# Step 7: Main function
def main():
    # Authenticate with the old server
    cookies = authenticate()
    if not cookies:
        print("Authentication failed. Exiting...")
        return

    # Fetch all scans (basic information)
    scans = fetch_all_scans(cookies)
    if not scans:
        print("No scans found or failed to fetch scans. Exiting...")
        return

    # Fetch detailed information for each scan
    detailed_scans = fetch_scan_details(scans, cookies)
    if not detailed_scans:
        print("Failed to fetch detailed information for scans. Exiting...")
        return

    # Save detailed scans to a JSON file
    save_detailed_scans(detailed_scans)

# Run the script
if __name__ == "__main__":
    main()
