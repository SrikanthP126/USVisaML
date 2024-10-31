import os
from azure.storage.blob import BlobServiceClient
from azure.identity import ManagedIdentityCredential
from logging import INFO, getLogger
from azure.monitor.opentelemetry import configure_azure_monitor

# Set up monitoring and logging
configure_azure_monitor()
logger = getLogger(__name__)
logger.setLevel(INFO)

def main(request_data: dict) -> dict:
    try:
        # Retrieve the filepath from request_data
        file_name = request_data.get("filepath")
        if not file_name:
            logger.error("Filepath not provided for download action")
            return {"status": "fail", "message": "Filepath not provided"}

        # Set up the BlobServiceClient
        container_name = os.getenv("BLOB_STORAGE_IDF_CONTAINER_NAME")
        blob_service_client = BlobServiceClient(
            account_url=os.getenv("BLOB_STORAGE_ACCOUNT_URL"),
            credential=ManagedIdentityCredential()
        )

        # Access the container and specific blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        if not blob_client.exists():
            logger.error("Specified file not found in Azure storage")
            return {"status": "fail", "message": "File not found in Azure storage"}

        # Define the local path to save the downloaded file
        local_path = f"/ark/landing_zone/downloads_from_azure/{os.path.basename(file_name)}"
        
        # Download the blob to the specified on-prem directory
        with open(local_path, "wb") as download_file:
            download_stream = blob_client.download_blob()
            download_file.write(download_stream.readall())

        logger.info(f"File '{file_name}' downloaded successfully to '{local_path}'")
        return {"status": "success", "message": f"File downloaded to {local_path}"}

    except Exception as e:
        logger.error(f"Error in BlobDownloadActivity: {str(e)}")
        return {"status": "fail", "message": str(e)}
