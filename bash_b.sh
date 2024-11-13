#!/bin/bash

# Define the destination directory and log file
DEST_DIR="/ark/landing_zone/idf"
LOG_FILE="/home/pj72693/IDF_Download_LOG/download_log_$(date '+%Y%m%d%H%M%S').log"

# Fetch the list of files from the Azure function and parse JSON to extract file names
file_list=$(curl -s -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=idf/submission" \
    -H 'accept: application/json' \
    --cert /ark/landing_zone/cert/azureappreg-ark-onprem-prod.pncint.net.pem \
    --pass 'Aopcc#24$')

# Convert JSON list of files into an array
file_list=($(echo "$file_list" | jq -r '.[]'))

# Loop through each file and download
for filename in "${file_list[@]}"; do
    echo "Downloading file: $filename" >> $LOG_FILE
    
    # Download the file using the HTTP function
    curl -v -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=idf/submission/$filename" \
        -H 'accept: application/json' \
        --output "${DEST_DIR}/${filename}" \
        --cert /ark/landing_zone/cert/azureappreg-ark-onprem-prod.pncint.net.pem \
        --pass 'Aopcc#24$'
    
    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo "Downloaded successfully: $filename" >> $LOG_FILE
    else
        echo "Error downloading file: $filename" >> $LOG_FILE
    fi
    echo "----------------------------------------" >> $LOG_FILE
done

echo "All files downloaded from Azure successfully" >> $LOG_FILE
