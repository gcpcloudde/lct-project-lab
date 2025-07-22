#!/bin/bash
echo "Taking existing bucket"
BUCKET_NAME="dev-dgmt127-bucket-1753195398" 
PUBSUB_TOPIC="gcs_bucket_notification_topic"
SUBSCRIPTION_NAME='gcs_bucket_notification_topic-sub'
 
echo "The following command creates a pubsub topic named $PUBSUB_TOPIC"
gcloud pubsub topics create $PUBSUB_TOPIC

echo "Creating subscription and attaching that to the topoic as well....."

gcloud pubsub subscriptions create $SUBSCRIPTION_NAME --topic=$PUBSUB_TOPIC

echo "The following creates the bucket notification on $BUCKET_NAME for pubsub topic $PUBSUB_TOPIC

gcloud storage buckets notifications create gs://$BUCKET_NAME --topic=$PUBSUB_TOPIC