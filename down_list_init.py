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
        # Retrieve Azure Storage details from environment variables
        container_name = os.getenv("BLOB_STORAGE_IDF_CONTAINER_NAME")
        blob_service_client = BlobServiceClient(
            account_url=os.getenv("BLOB_STORAGE_ACCOUNT_URL"),
            credential=ManagedIdentityCredential()
        )

        # Access the container client
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()

        # Prepare list of blob details
        files = []
        for blob in blob_list:
            files.append({
                "file_name": blob.name,
                "size_in_bytes": blob.size,
                "last_modified": str(blob.last_modified)
            })

        logger.info(f"Listed {len(files)} files in the container")
        return {"status": "success", "files": files}

    except Exception as e:
        logger.error(f"Error in BlobListingActivity: {str(e)}")
        return {"status": "fail", "message": str(e)}
