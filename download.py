from datetime import datetime
import os
import logging
import traceback
import json
import azure.functions as func
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import ManagedIdentityCredential
import aiohttp
import re

blobServiceClient = None

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get folder path from request
        path = req.params.get('name')
        if not path:
            try:
                req_body = req.get_json()
                path = req_body.get('name')
            except ValueError:
                pass

        if path:
            timeStartGet = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
            logging.info("Start Get File "+ path +" "+ timeStartGet)
            
            #azure Connection
            azure_container_name = 'a360root'
            
            global blobServiceClient
            if blobServiceClient == None:
                blobServiceClient = BlobServiceClient(
                    os.environ.get("BLOB_STORAGE_ACCOUNT_URL"),
                    credential=ManagedIdentityCredential()
                )

            # Get container client
            container_client = blobServiceClient.get_container_client(azure_container_name)
            
            # List all blobs in the specified folder
            blob_list = []
            async for blob in container_client.list_blobs(name_starts_with=path):
                blob_list.append(blob.name)

            if blob_list:
                # Download all files
                downloaded_files = []
                for blob_name in blob_list:
                    blob_client = container_client.get_blob_client(blob_name)
                    if await blob_client.exists():
                        downloader = await blob_client.download_blob()
                        content = await downloader.readall()
                        downloaded_files.append({
                            'name': blob_name,
                            'content': content.decode('utf-8', errors='ignore')
                        })

                timeEndGet = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
                
                headers = {
                    "Content-Type": "application/json",
                    "Logs": f"Files from folder {path} downloaded at {timeStartGet} to {timeEndGet}"
                }

                return func.HttpResponse(
                    json.dumps({
                        "status": "success",
                        "files": downloaded_files,
                        "count": len(downloaded_files)
                    }),
                    headers=headers,
                    status_code=200
                )
            else:
                timeFileNotFound = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
                headers = {
                    "Logs": f"Folder {path} " + timeFileNotFound + " AzureFileNotFound "
                }
                return func.HttpResponse(
                    json.dumps({
                        "status": "fail",
                        "errdesc": "File Not Found"
                    }),
                    headers=headers,
                    status_code=404
                )
        else:
            return func.HttpResponse(
                json.dumps({
                    "status": "fail",
                    "errdesc": "You need to pass the parameter 'name' to download the files"
                }),
                status_code=400
            )
            
    except Exception:
        return func.HttpResponse(
            json.dumps({
                "status": "fail",
                "errdesc": traceback.format_exc()
            }),
            status_code=500,
            mimetype='application/json'
        )
