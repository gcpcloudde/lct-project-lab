#!/bin/bash

PROJECT_ID="lhn-dev-project"
BUCKET_NAME="prod-test-bucket-$(date +%s)"
LOCATION="us-central1"
STORAGE_CLASS="STANDARD"

echo "Creating GCS bucket: $BUCKET_NAME in project: $PROJECT_ID"
echo "new one"
gcloud storage buckets create gs://$BUCKET_NAME \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --default-storage-class=$STORAGE_CLASS
