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
import pathlib

blobServiceClient = None

async def create_download_directory(base_path):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        download_path = os.path.join(base_path, today)
        os.makedirs(download_path, exist_ok=True)
        logging.info(f"Created directory: {download_path}")
        return download_path
    except Exception as e:
        logging.error(f"Error creating directory: {str(e)}")
        raise

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get folder path and local download path from request
        path = req.params.get('name')
        local_path = req.params.get('download_path', '/tmp/downloads')
        
        # Log incoming request details
        logging.info(f"Received request - Path: {path}, Local path: {local_path}")
        
        if not path:
            try:
                req_body = req.get_json()
                path = req_body.get('name')
                local_path = req_body.get('download_path', '/tmp/downloads')
                logging.info(f"Retrieved from body - Path: {path}, Local path: {local_path}")
            except ValueError:
                logging.error("Failed to parse request body")
                pass

        if path:
            timeStartGet = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
            logging.info(f"Start Get File {path} at {timeStartGet}")
            
            download_dir = await create_download_directory(local_path)
            
            azure_container_name = 'a360root'
            
            global blobServiceClient
            if blobServiceClient == None:
                connection_string = os.environ.get("BLOB_STORAGE_ACCOUNT_URL")
                if not connection_string:
                    logging.error("BLOB_STORAGE_ACCOUNT_URL environment variable not set")
                    return func.HttpResponse(
                        json.dumps({
                            "status": "fail",
                            "errdesc": "Azure storage connection string not configured"
                        }),
                        status_code=500
                    )
                    
                blobServiceClient = BlobServiceClient(
                    connection_string,
                    credential=ManagedIdentityCredential()
                )
                logging.info("Successfully created BlobServiceClient")

            container_client = blobServiceClient.get_container_client(azure_container_name)
            logging.info(f"Accessing container: {azure_container_name}")
            
            blob_list = []
            try:
                async for blob in container_client.list_blobs(name_starts_with=path):
                    blob_list.append(blob.name)
                logging.info(f"Found {len(blob_list)} blobs in path {path}")
            except Exception as e:
                logging.error(f"Error listing blobs: {str(e)}")
                return func.HttpResponse(
                    json.dumps({
                        "status": "fail",
                        "errdesc": f"Error accessing Azure storage: {str(e)}"
                    }),
                    status_code=500
                )

            if blob_list:
                downloaded_files = []
                for blob_name in blob_list:
                    try:
                        blob_client = container_client.get_blob_client(blob_name)
                        if await blob_client.exists():
                            local_file_name = os.path.basename(blob_name)
                            local_file_path = os.path.join(download_dir, local_file_name)
                            
                            downloader = await blob_client.download_blob()
                            content = await downloader.readall()
                            
                            with open(local_file_path, 'wb') as file:
                                file.write(content)
                            
                            downloaded_files.append({
                                'name': blob_name,
                                'local_path': local_file_path
                            })
                            logging.info(f"Successfully downloaded: {blob_name}")
                    except Exception as e:
                        logging.error(f"Error downloading blob {blob_name}: {str(e)}")
                        continue

                timeEndGet = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
                
                headers = {
                    "Content-Type": "application/json",
                    "Logs": f"Files from folder {path} downloaded at {timeStartGet} to {timeEndGet}"
                }

                return func.HttpResponse(
                    json.dumps({
                        "status": "success",
                        "files": downloaded_files,
                        "count": len(downloaded_files),
                        "download_directory": download_dir
                    }),
                    headers=headers,
                    status_code=200
                )
            else:
                timeFileNotFound = datetime.utcnow().isoformat(sep=" ", timespec="milliseconds")
                error_message = f"No files found in path: {path}"
                logging.warning(error_message)
                headers = {
                    "Logs": f"Folder {path} {timeFileNotFound} AzureFileNotFound"
                }
                return func.HttpResponse(
                    json.dumps({
                        "status": "fail",
                        "errdesc": error_message,
                        "path_searched": path,
                        "container": azure_container_name
                    }),
                    headers=headers,
                    status_code=404
                )
        else:
            error_message = "Missing required parameter 'name'"
            logging.error(error_message)
            return func.HttpResponse(
                json.dumps({
                    "status": "fail",
                    "errdesc": error_message
                }),
                status_code=400
            )
            
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Unexpected error: {error_details}")
        return func.HttpResponse(
            json.dumps({
                "status": "fail",
                "errdesc": str(e),
                "stack_trace": error_details
            }),
            status_code=500,
            mimetype='application/json'
        )
