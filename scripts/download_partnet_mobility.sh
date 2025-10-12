#!/bin/bash
set -e
set -o pipefail

#
# Example usage: bash download_partnet_mobility.sh --objects_id 3763 3380 --token <token>
# To get an access token register here: https://sapien.ucsd.edu/downloads, then copy on any download link
# and you'll find the token there: https://sapien.ucsd.edu/api/download/partnet-mobility-v0.zip?token=<token>
# You can pass in multiple object IDs found here: https://sapien.ucsd.edu/browse
#


# Check if unzip is already installed
if ! command -v unzip &> /dev/null; then
    echo "unzip not found, installing..."
    apt-get update
    apt-get install -y unzip
fi


DATASET_PATH="/workspace/RoboSandbox/temp_data/PartNet-Mobility"
BASE_URL="https://sapien.ucsd.edu/api/download/compressed"
OBJECT_IDS=()
TOKEN=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --objects_id)
            shift
            while [[ "$#" -gt 0 && "$1" != --* ]]; do OBJECT_IDS+=("$1"); shift; done
            ;;
        --token)
            shift
            TOKEN="$1"
            shift
            ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
done

if [ ${#OBJECT_IDS[@]} -eq 0 ]; then
    echo "No object IDs provided. Usage: bash $0 --objects_id 3763 3380 --token <token>"
    exit 1
fi
if [ -z "$TOKEN" ]; then
    echo "No token provided. Usage: bash $0 --objects_id 3763 3380 --token <token>"
    exit 1
fi

mkdir -p "$DATASET_PATH"

# Download and unzip object
for OBJ in "${OBJECT_IDS[@]}"; do
    TARGET_DIR="${DATASET_PATH}/${OBJ}"
    ZIP_PATH="${DATASET_PATH}/${OBJ}.zip"
    DOWNLOAD_URL="${BASE_URL}/${OBJ}.zip?token=${TOKEN}"
    if [ -d "$TARGET_DIR" ]; then  # if dir already exists skip redownload
        continue
    fi
    if wget -q -O "$ZIP_PATH" "$DOWNLOAD_URL"; then
        mkdir -p "$TARGET_DIR"
        if unzip -o -q "$ZIP_PATH" -d "${DATASET_PATH}"; then
            rm -f "$ZIP_PATH"
        else
            echo "Failed to unzip $OBJ"
        fi
    else
        echo "Could not download object $OBJ"
    fi
done

echo "Done downloading objects"
