import os
import logging
import traceback
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import ManagedIdentityCredential
from datetime import datetime
import aiohttp

blobServiceClient = None
containerClient = None

async def main(req: func.HttpRequest) -> func.HttpResponse:
    blob_name = ""
    timeStartPost = datetime.utcnow().isoformat(sep='T', timespec='milliseconds')
    timeEndPost = ""
    fileByteArray = None
    try:
        # Fetch the file path from the request parameters
        filepath = req.params.get('filepath')
        
        # Iterate through the uploaded files
        for key, value in req.files.items():
            if filepath and filepath != "":
                blob_name = filepath
            else:
                blob_name = key
            
            # Log the start time and file being uploaded
            timeStartPost = datetime.utcnow().isoformat(sep='T', timespec="milliseconds")
            logging.info("Start Post File : " + blob_name + " at " + timeStartPost)
            
            # Read the file data as bytes
            fileByteArray = await value.read()  # Fixed: Properly read file as bytes
            
        global blobServiceClient, containerClient
        
        # Initialize the BlobServiceClient if not already done
        if blobServiceClient is None:
            logging.info("New Connection GET BlobServiceClient")
            blobServiceClient = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=staarkaze2022;AccountKey=YourAccountKeyHere;EndpointSuffix=core.windows.net")
        
        # Get the container client for the "oimreport" container
        containerClient = blobServiceClient.get_container_client("oimreport")
        
        if containerClient is None:
            logging.info("New Connection GET ContainerClient")
            containerClient = blobServiceClient.get_container_client("oimreport")
        
        # Upload the file to the specified container
        await containerClient.upload_blob(name=blob_name, data=fileByteArray, overwrite=True)
        
        timeEndPost = datetime.utcnow().isoformat(sep='T', timespec='milliseconds')
        logging.info("End Post File : " + blob_name + " at " + timeEndPost)
        
        # Return success response
        resp = {"status": "success", "file": blob_name, "size": len(fileByteArray), "timeEndPost": timeEndPost, "timeStartPost": timeStartPost}
        return func.HttpResponse(json.dumps(resp), status_code=200, mimetype='application/json')
    
    except Exception as ex:
        # Log the error and return a failure response
        logging.info("Error : " + traceback.format_exc())
        resp = {"status": "fail", "error": traceback.format_exc()}
        return func.HttpResponse(json.dumps(resp), status_code=500, mimetype='application/json')
