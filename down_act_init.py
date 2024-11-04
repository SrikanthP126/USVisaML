import os
from azure.storage.blob import BlobServiceClient
import logging

# Configure logger
configure_azure_monitor()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Path to the tracking file
TRACKING_FILE_PATH = "/ark/landing_zone/downloaded_files.txt"

def load_downloaded_files():
    """Load the list of already downloaded files from the tracking file."""
    if os.path.exists(TRACKING_FILE_PATH):
        with open(TRACKING_FILE_PATH, "r") as file:
            return set(line.strip() for line in file)
    return set()

def update_downloaded_files(new_files):
    """Append newly downloaded files to the tracking file."""
    with open(TRACKING_FILE_PATH, "a") as file:
        for file_name in new_files:
            file.write(f"{file_name}\n")

def main(input: dict) -> dict:
    try:
        # Use the connection string for authentication
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("BLOB_STORAGE_IDF_CONTAINER_NAME")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        filepath = input.get("filepath")
        if not filepath:
            logger.error("Filepath not provided for download action")
            return {"status": "fail", "message": "Filepath not provided"}

        # Load previously downloaded files
        downloaded_files = load_downloaded_files()

        container_client = blob_service_client.get_container_client(container_name)
        blobs = container_client.list_blobs(name_starts_with=filepath)

        new_files = []  # To track files downloaded in this session
        for blob in blobs:
            file_name = blob.name.split("/")[-1]  # Extract the file name from the path

            # Skip files that have already been downloaded
            if file_name in downloaded_files:
                logger.info(f"Skipping already downloaded file: {file_name}")
                continue

            # Define local path for the new file
            local_path = f"/ark/landing_zone/downloads_from_azure/{file_name}"
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
            
            # Download the new file
            with open(local_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            new_files.append(file_name)
            logger.info(f"File '{file_name}' downloaded successfully to '{local_path}'")

        # Update the tracking file with newly downloaded files
        update_downloaded_files(new_files)

        return {
            "status": "success",
            "message": f"Newly downloaded files: {new_files}"
        }

    except Exception as e:
        logger.error(f"Error in BlobDownloadActivity: {str(e)}")
        return {"status": "fail", "message": str(e)}
