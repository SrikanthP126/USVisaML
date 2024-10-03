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
        filepath = req.params.get('filepath')
        for key, value in req.files.items():
            if filepath and filepath != "":
                blob_name = filepath
            else:
                blob_name = key
            timeStartPost = datetime.utcnow().isoformat(sep='T', timespec="milliseconds")
            logging.info("Start Post File : " + blob_name + " at " + timeStartPost)
            fileByteArray = value.stream.read()

        global blobServiceClient, containerClient

        if blobServiceClient is None:
            logging.info("New Connection GET BlobServiceClient")
            blobServiceClient = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=staarkaze2022;AccountKey=YourAccountKeyHere;EndpointSuffix=core.windows.net")

        # Change to "oimreport" container
        containerClient = blobServiceClient.get_container_client("oimreport")

        if containerClient is None:
            logging.info("New Connection GET ContainerClient")
            containerClient = blobServiceClient.get_container_client("oimreport")

        await containerClient.upload_blob(name=blob_name, data=fileByteArray, overwrite=True)
        timeEndPost = datetime.utcnow().isoformat(sep='T', timespec='milliseconds')
        logging.info("End Post File : " + blob_name + " at " + timeEndPost)
        resp = {"status": "success", "file": blob_name, "size": len(fileByteArray), "timeEndPost": timeEndPost, "timeStartPost": timeStartPost}
        return func.HttpResponse(json.dumps(resp), status_code=200, mimetype='application/json')
    
    except Exception as ex:
        logging.info("Error : " + traceback.format_exc())
        resp = {"status": "fail", "error": traceback.format_exc()}
        return func.HttpResponse(json.dumps(resp), status_code=500, mimetype='application/json')
