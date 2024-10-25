import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from azure.storage.blob.aio import BlobServiceClient

# Configure logging to Log Analytics
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=YOUR_INSTRUMENTATION_KEY"))

async def main(blobdata: dict):
    try:
        blob_name = blobdata['blob_name']
        filepath = blobdata['filepath']

        logger.info(f"Uploading file {blob_name} from path {filepath}")

        with open(filepath, "rb") as file:
            fileByteArray = file.read()

        connection_string = "DefaultEndpointsProtocol=..."
        blobServiceClient = BlobServiceClient.from_connection_string(connection_string)

        container_name = "oimreports"
        containerClient = blobServiceClient.get_container_client(container_name)

        await containerClient.upload_blob(name=blob_name, data=fileByteArray, overwrite=True)

        logger.info(f"File {blob_name} uploaded successfully from {filepath}")
        return {"status": "success", "file": blob_name}

    except Exception as ex:
        logger.error(f"Error in activity function: {str(ex)}")
        return {"status": "fail", "errdesc": str(ex)}
