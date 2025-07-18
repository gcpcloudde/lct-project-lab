#!/bin/bash
PROJECT_ID="lhn-dev-project"
BUCKET_NAME="dev-bucket-$(date +%s)"
LOCATION="us-central1"
STORAGE_CLASS="STANDARD"

gcloud storage buckets create gs://$BUCKET_NAME \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --storage-class=$STORAGE_CLASS
