# Get the list of files in /NLD/ directory
file_list=$(curl -s -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/listfiles?directory=NLD" \
    -H 'accept: application/json' \
    --cert /home/pj72693/azureappreg-ark-deployment-pipeline-qa.pncint.net.pem \
    --pass 'Rydd#17$')

# Convert JSON response to an array of file names (assuming JSON array response)
file_list=($(echo $file_list | jq -r '.[]')) # Requires 'jq' to parse JSON

for filename in "${file_list[@]}"; do
    echo "Downloading file: $filename" >> $LOG_FILE
    curl -v -X 'GET' "https://func-ark-prod-aze2.azurewebsites.net/api/getfile?name=download/NLD/${filename}" \
        -H 'accept: application/json' \
        --output "${DEST_DIR}/${filename}" \
        --cert /home/pj72693/azureappreg-ark-deployment-pipeline-qa.pncint.net.pem \
        --pass 'Rydd#17$'

    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo "Downloaded successfully: $filename" >> $LOG_FILE
    else
        echo "Error downloading file: $filename" >> $LOG_FILE
    fi
done
