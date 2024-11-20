#!/bin/bash

# Metadata and Configuration
metadata_file="/ark/landing_zone/idf/Renamed_Manifests.txt"
DEST_DIR="/ark/landing_zone/idf/submission_11192024"
CERT_PATH="/ark/landing_zone/cert/azureappreg-ark-onprem-prod.pncint.net.pem"
PASS="Aopcc#24$"
LOG_FILE="/ark/landing_zone/idf/download_log_$(date +%Y%m%d).log"

# Function to log messages
log_message() {
  local message="$1"
  echo "$(date +'%Y-%m-%d %H:%M:%S') : $message" | tee -a "$LOG_FILE"
}

# Start processing
log_message "Download process started."

# Loop through metadata file to download files
while IFS= read -r line; do
  file_path=$(echo "$line" | awk '{print $2}')
  if [[ "$file_path" =~ ^idf/response/[^/]+\.[^.]+$ ]]; then
    filename_only=$(basename "$file_path")
    log_message "Attempting to download file: $file_path"
    
    curl -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=$file_path" \
      -H 'accept: application/json' \
      --output "${DEST_DIR}/${filename_only}" \
      --cert "$CERT_PATH" \
      --pass "$PASS"

    if [[ $? -eq 0 ]]; then
      log_message "Successfully downloaded: ${filename_only}"
    else
      log_message "Failed to download: ${filename_only}"
    fi
  else
    log_message "Skipping invalid file path: $file_path"
  fi

done < "$metadata_file"

log_message "Download process completed."
