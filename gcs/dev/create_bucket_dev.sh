#!/bin/bash

#!/bin/bash

# Set variables
PROJECT_ID="lhn-dev-project"
SRC_BUCKET="prod-dmgt123-bucket-1752939743"
DEST_BUCKET="prod-dmgt124-bucket-1752940679"
LOCATION="us-central1"
STORAGE_CLASS="STANDARD"


# Copy all objects from source to destination
echo "Copying objects from gs://$SRC_BUCKET to gs://$DEST_BUCKET"
gcloud storage cp --recursive gs://$SRC_BUCKET gs://$DEST_BUCKET

# Uncomment the following if you want to delete the original files after copying (i.e., move instead of copy)
# echo "Deleting original objects from gs://$SRC_BUCKET"
# gcloud storage rm --recursive gs://$SRC_BUCKET