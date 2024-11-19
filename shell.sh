#!/bin/bash

LOG_FILE="/ark/landing_zone/tdf/script_logs/download_response_files.log"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

METADATA_FILE_BASE="response_files_list_${TIMESTAMP}.txt"
METADATA_FILE="/ark/landing_zone/tdf/${METADATA_FILE_BASE}"
DEST_DIR_BASE="response_files_list_${TIMESTAMP}"
DEST_DIR="/ark/landing_zone/tdf/${DEST_DIR_BASE}"

CERT_PATH="/ark/landing_zone/cert/azureappreg-ark-onprem-prod.pnctnt.net.pem"
PASS="Aopcc#24$"

# Create destination directory
mkdir -p "$DEST_DIR"

# Download metadata file
echo "$(date +"%Y-%m-%d %H:%M:%S") - Fetching metadata file: $METADATA_FILE_BASE" >> "$LOG_FILE"
curl -X 'GET' \
    "https://func-ark-prod-aze2.azurewebsites.net/api/ARK_FileInfo_OnPrem?filenamestartswithidf/response" \
    -H 'accept: application/json' \
    --cert "$CERT_PATH" \
    --pass "$PASS" \
    --output "$METADATA_FILE"

if [[ ! -f "$METADATA_FILE" ]]; then
    echo "$(date +"%Y-%m-%d %H:%M:%S") - Failed to download response file." >> "$LOG_FILE"
    exit 1
fi

echo "$(date +"%Y-%m-%d %H:%M:%S") - Successfully downloaded response file." >> "$LOG_FILE"

# Process each line in the metadata file
while IFS= read -r line; do
    file_path=$(echo "$line" | awk '{print $2}')

    if [[ "$file_path" =~ ^idf/response/[^/]+\.[^/]+$ ]]; then
        filename_only=$(basename "$file_path")
        
        echo "$(date +"%Y-%m-%d %H:%M:%S") - Downloading file: $filename_only to $DEST_DIR" >> "$LOG_FILE"
        curl -X 'GET' \
            "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=$file_path" \
            -H 'accept: application/json' \
            --cert "$CERT_PATH" \
            --pass "$PASS" \
            --output "$DEST_DIR/${filename_only}"

        if [ $? -eq 0 ]; then
            echo "$(date +"%Y-%m-%d %H:%M:%S") - Successfully downloaded $filename_only" >> "$LOG_FILE"
        else
            echo "$(date +"%Y-%m-%d %H:%M:%S") - Failed to download $filename_only" >> "$LOG_FILE"
        fi
    else
        echo "$(date +"%Y-%m-%d %H:%M:%S") - Invalid file path format: $file_path" >> "$LOG_FILE"
    fi
done < "$METADATA_FILE"
