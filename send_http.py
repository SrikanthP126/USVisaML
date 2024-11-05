import os
import hashlib
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
from datetime import datetime, timedelta

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Set container name and blob name directly for now
        container_name = "<your-container-name>"  # Replace with your container name
        blob_name = req.params.get("filepath")
        chunk_size = 100 * 1024 * 1024  # 100 MB

        # Initialize BlobServiceClient with the hardcoded connection string
        blob_service_client = BlobServiceClient.from_connection_string(
            "DefaultEndpointsProtocol=https;AccountName=<your-account-name>;AccountKey=<your-account-key>;EndpointSuffix=core.windows.net"
        )
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Download and chunk the file
        blob_size = (await blob_client.get_blob_properties()).size
        file_parts = []
        part_number = 0

        # Create a temp file path for chunks
        temp_dir = "/tmp"
        temp_file_path = os.path.join(temp_dir, blob_name)

        # Download in chunks and store parts temporarily
        for start_byte in range(0, blob_size, chunk_size):
            end_byte = min(start_byte + chunk_size - 1, blob_size - 1)
            range_header = f"bytes={start_byte}-{end_byte}"

            # Download the chunk
            stream = await blob_client.download_blob(offset=start_byte, length=(end_byte - start_byte + 1))
            part_path = f"{temp_file_path}.part{part_number}"
            with open(part_path, "wb") as chunk_file:
                chunk_file.write(await stream.readall())

            file_parts.append(part_path)
            part_number += 1

        # Merge chunks into a single file
        merged_file_path = f"{temp_file_path}_merged"
        with open(merged_file_path, "wb") as merged_file:
            for part_path in file_parts:
                with open(part_path, "rb") as chunk_file:
                    merged_file.write(chunk_file.read())
                os.remove(part_path)  # Clean up chunk files after merging

        # Hash Validation
        sha256_hash = hashlib.sha256()
        with open(merged_file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()

        # Return the final file path and hash
        response = {
            "status": "success",
            "file_path": merged_file_path,
            "file_hash": file_hash
        }
        return func.HttpResponse(json.dumps(response), status_code=200, mimetype="application/json")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return func.HttpResponse(
            json.dumps({"status": "fail", "error": error_message}),
            status_code=500,
            mimetype="application/json"
        )
