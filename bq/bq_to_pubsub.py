import time
import json
import random
from datetime import datetime
from decimal import Decimal
from google.cloud import bigquery
from google.cloud import pubsub_v1

# === CONFIGURATION ===
BQ_QUERY = """
    SELECT 
        pickup_datetime, 
        dropoff_datetime, 
        passenger_count, 
        trip_distance, 
        fare_amount, 
        payment_type 
    FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2018`
    WHERE fare_amount > 0
    LIMIT 1000
"""

PROJECT_ID = "lhn-dev-project"  # Replace this
PUBSUB_TOPIC = "nyc-taxi-topic"     # Replace this

# === HANDLE datetime and Decimal ===
def convert_row(row):
    converted = {}
    for key, value in dict(row).items():
        if isinstance(value, datetime):
            converted[key] = value.isoformat()
        elif isinstance(value, Decimal):
            converted[key] = float(value)
        else:
            converted[key] = value
    return converted

# === FETCH DATA ===
def fetch_bigquery_data():
    client = bigquery.Client()
    query_job = client.query(BQ_QUERY)
    results = query_job.result()
    rows = [convert_row(row) for row in results]
    return rows

# === PUBLISH MESSAGES ===
def publish_messages(data_rows):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

    print(f"Publishing to {topic_path} every 3–5 seconds...\n")

    for row in data_rows:
        message_json = json.dumps(row)
        message_bytes = message_json.encode("utf-8")

        future = publisher.publish(topic_path, data=message_bytes)
        print(f"Published: {message_json}")

        time.sleep(random.randint(45,60))

    print("Finished publishing.")

# === MAIN ===
if __name__ == "__main__":
    print("Fetching data from BigQuery...\n")
    data = fetch_bigquery_data()
    print(f"Fetched {len(data)} rows.\n")

    publish_messages(data)
