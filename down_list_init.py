import os
from azure.storage.blob import BlobServiceClient
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main(input: dict) -> dict:
    try:
        # Directly setting up the connection string and container name from code
        connection_string = "DefaultEndpointsProtocol=https;AccountName=staarkaze2022;AccountKey=YOUR_ACCOUNT_KEY_HERE;EndpointSuffix=core.windows.net"
        container_name = "a360root"

        # Initialize BlobServiceClient using the provided connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # List all blobs in the container
        blob_list = container_client.list_blobs()
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
