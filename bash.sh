#!/bin/bash

# Exporting required variables
export PGM="DownloadFilesFromAzureToOnPrem"
export DATETIME=$(date "+%Y%m%d%H%M%S")
export LOG_DIR=/home/jp72693/IDF_LOG
export LOG_FILE=${LOG_DIR}/${PGM}_${DATETIME}.log

# Starting the download process
echo "Starting $PGM Main Code" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE

# Directory to store downloaded files
DEST_DIR="/ark/landing_zone/idf"

# Looping through each file to download from Azure Blob Storage
for file in /path/to/filelist/*; do
    export filename_only=$(basename "$file")
    echo "Downloading file: $filename_only" >> $LOG_FILE
    echo "########################################" >> $LOG_FILE
    echo "$(date)" >> $LOG_FILE

    # Trigger Azure HTTP download function
    curl -v -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/ARK_FileInfo_OnPrem?filenamestartswith=idfdownload/${filename_only}" \
        -H 'accept: application/json' \
        --output "${DEST_DIR}/${filename_only}" \
        --cert /ark/landing_zone/cert/azureappreg-ark-onprem-prod.pncint.net.pem \
        --pass 'Aopcc#24$'

    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo "Downloaded successfully: $filename_only" >> $LOG_FILE
    else
        echo "Error downloading file: $filename_only" >> $LOG_FILE
    fi

    echo "$(date)" >> $LOG_FILE
    echo "----------------------------------------" >> $LOG_FILE
done

echo "All files downloaded from Azure successfully" >> $LOG_FILE
echo "$(date)" >> $LOG_FILE
