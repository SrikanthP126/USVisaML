import requests
import json
from urllib.parse import quote

# Constants
MX_IP_ADDRESS = "your_old_server_ip"  # Replace with the old server IP or domain
AUTH_ENDPOINT = f"https://{MX_IP_ADDRESS}:8083/SecureSphere/api/v1/auth/session"
SCAN_NAMES_ENDPOINT = f"https://{MX_IP_ADDRESS}:8083/SecureSphere/api/v1/conf/assessment/scans"
SCAN_DETAILS_ENDPOINT = f"https://{MX_IP_ADDRESS}:8083/SecureSphere/api/v1/conf/assessment/scans"

# Authentication
def authenticate():
    """Authenticate with the old server and return session cookies."""
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(AUTH_ENDPOINT, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            print("Authentication successful!")
            return response.cookies
        else:
            print(f"Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

# Step 1: Fetch and filter scan names
def fetch_and_filter_scan_names(cookies):
    """Fetch all scan names and filter by 'DataRetention' keyword."""
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(SCAN_NAMES_ENDPOINT, headers=headers, cookies=cookies, verify=False)
        if response.status_code == 200:
            # Parse response JSON
            all_scans = response.json()

            # Validate response structure
            if isinstance(all_scans, list):
                # Filter only 'DataRetention' scans
                filtered_scans = []
                for scan in all_scans:
                    if isinstance(scan, dict):  # Ensure each item is a dictionary
                        if "DataRetention" in scan.get("name", ""):
                            filtered_scans.append(scan)
                    else:
                        print(f"Skipping invalid scan entry: {scan}")

                # Remove duplicates
                unique_scans = list({scan["name"]: scan for scan in filtered_scans}.values())
                with open("scans_DataRetention.json", "w") as file:
                    json.dump(unique_scans, file, indent=4)
                print(f"Saved {len(unique_scans)} filtered scans to scans_DataRetention.json.")
                return unique_scans
            else:
                print("Unexpected response format: Not a list.")
                return []
        else:
            print(f"Failed to fetch scan names: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching scan names: {e}")
        return []



# Step 2: Fetch detailed metadata
def fetch_detailed_metadata(filtered_scans, cookies):
    """Fetch detailed metadata for each filtered scan."""
    headers = {"Content-Type": "application/json"}
    detailed_scans = []
    failed_scans = []

    for scan in filtered_scans:
        try:
            scan_name = scan["name"]
            print(f"Fetching details for: {scan_name}")
            encoded_name = quote(scan_name)  # URL encode the scan name
            url = f"{SCAN_DETAILS_ENDPOINT}/{encoded_name}"
            response = requests.get(url, headers=headers, cookies=cookies, verify=False)
            if response.status_code == 200:
                detailed_scans.append(response.json())
            else:
                failed_scans.append(scan_name)
                print(f"Failed to fetch details for {scan_name}: {response.status_code}")
        except Exception as e:
            failed_scans.append(scan_name)
            print(f"Error fetching details for {scan_name}: {e}")

    # Save detailed and failed scans
    with open("detailed_DataRetention_scans.json", "w") as file:
        json.dump(detailed_scans, file, indent=4)
    with open("failed_DataRetention_scans.json", "w") as file:
        json.dump(failed_scans, file, indent=4)
    print("Saved detailed and failed scans.")

# Main workflow
def main():
    cookies = authenticate()
    if not cookies:
        print("Authentication failed.")
        return

    # Step 1: Fetch and filter scan names
    filtered_scans = fetch_and_filter_scan_names(cookies)

    # Step 2: Fetch detailed metadata
    fetch_detailed_metadata(filtered_scans, cookies)

if __name__ == "__main__":
    main()
