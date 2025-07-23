
#!/bin/bash

# --- Configurable Variables ---
PROJECT_ID="your-project-id"
BUCKET_NAME="gcs_bucket_notification_demo"
TOPIC_NAME="gcs-bucket-notification-topic"

# --- Set the project ---
gcloud config set project "$PROJECT_ID"

# --- Create the Pub/Sub topic ---
echo "Creating Pub/Sub topic: $TOPIC_NAME"
gcloud pubsub topics create "$TOPIC_NAME" --project="$PROJECT_ID"

# --- Add a GCS notification to the bucket for OBJECT_FINALIZE events ---
echo "Creating GCS bucket notification for bucket: $BUCKET_NAME"
gsutil notification create -t "$TOPIC_NAME" -f json -e OBJECT_FINALIZE gs://"$BUCKET_NAME"

echo "✅ GCS Notification setup completed."
