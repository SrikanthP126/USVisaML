import requests
import base64
import getpass
import json

# Step 1: Define the server details
MX_IP_ADDRESS = "your_server_ip_or_domain"  # Replace with your MX server IP or domain
AUTH_ENDPOINT = f"https://{MX_IP_ADDRESS}:8083/SecureSphere/api/v1/auth/session"
SCANS_ENDPOINT = f"https://{MX_IP_ADDRESS}:8083/SecureSphere/api/v1/scans"

# Step 2: Provide credentials for authentication
USERNAME = input("Enter your username: ")
PASSWORD = getpass.getpass("Enter your password (input will be hidden): ")

# Step 3: Encode the credentials in Base64
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

# Step 4: Set up headers for API requests
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

# Step 5: Authenticate with the server
def authenticate():
    try:
        print("Authenticating...")
        response = requests.post(AUTH_ENDPOINT, headers=headers, verify=False)  # Set verify=False if SSL issues
        if response.status_code == 200:
            print("Authentication successful!")
            return response.cookies  # Return session cookies for subsequent requests
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

# Step 6: Fetch scans from the server
def fetch_scans(cookies):
    try:
        print("Fetching scans...")
        response = requests.get(SCANS_ENDPOINT, headers=headers, cookies=cookies, verify=False)
        if response.status_code == 200:
            scans = response.json()
            print(f"Successfully retrieved {len(scans)} scans.")
            # Save the scans to a JSON file for later use
            with open("scans.json", "w") as file:
                json.dump(scans, file, indent=4)
            print("Scans saved to scans.json")
        else:
            print(f"Failed to fetch scans: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error during fetching scans: {e}")

# Step 7: Main function to orchestrate the steps
def main():
    cookies = authenticate()
    if cookies:
        fetch_scans(cookies)
    else:
        print("Authentication failed. Exiting...")

# Run the script
if __name__ == "__main__":
    main()
