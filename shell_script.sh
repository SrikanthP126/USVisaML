#!/bin/bash

# Configuration
metadata_file="/ark/landing_zone/ldf/response/Renamed_Manifests.txt"
dest_dir="/ark/landing_zone/ldf/submission/"
cert_path="/ark/landing_zone/cert/azureppreg-ark-onprem-prod.pnclnt.net.pem"
pass="Aoocc#245"

# Check if metadata file exists
if [ ! -f "$metadata_file" ]; then
    echo "Error: Metadata file not found: $metadata_file"
    exit 1
fi

# Check if destination directory exists, if not create it
if [ ! -d "$dest_dir" ]; then
    mkdir -p "$dest_dir"
fi

# Process each line in the metadata file
while IFS= read -r line; do
    # Extract file path using awk
    file_path=$(echo "$line" | awk '{print $2}')
    
    # Check if the file path matches the pattern
    if [[ "$file_path" =~ ^ldf/submission/[^/]+\.[^\.]+$ ]]; then
        # Extract filename from path
        filename_only=$(basename "$file_path")
        
        echo "Downloading: $filename_only"
        
        # Perform the curl download
        curl -X 'GET' \
             "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=$file_path" \
             -H 'accept: application/json' \
             --output "${dest_dir}/${filename_only}" \
             --cert "$cert_path" \
             --pass "$pass" \
             --silent --show-error --fail
        
        # Check if download was successful
        if [ $? -eq 0 ]; then
            echo "Successfully downloaded: $filename_only"
        else
            echo "Failed to download: $filename_only"
        fi
    fi
done < "$metadata_file"

echo "Download process completed"
