from airflow import models
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator

from datetime import timedelta

# Constants
PROJECT_ID = "lhn-dev-project"
LOCATION = "us-central1"
GCS_TEMPLATE_PATH = "gs://dataflow-flex-template-ex-demo/gcstobqload.json"

with models.DAG(
    dag_id="dataflow_flex_template_input_output",
    schedule_interval="*/10 * * * *",  # Trigger manually or set cron job - This is set up with cron job to run every 10 minutes
    start_date=days_ago(1),
    catchup=False,
    default_args={
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["example", "dataflow", "flex-template"],
) as dag:

    start_flex_template_job = DataflowStartFlexTemplateOperator(
        task_id="run_dataflow_flex_template",
        project_id=PROJECT_ID,
        location=LOCATION,
        body={
            "launchParameter": {
                "jobName": "flex-job-{{ ds_nodash }}",
                "containerSpecGcsPath": GCS_TEMPLATE_PATH,
                "parameters": {
                    "input": "gs://sample-bucket-etl-job-demo/sample1000.csv",
                    "output_table": "lhn-dev-project.us_tax_rides.tax_rides",
                    "invalid_table": "lhn-dev-project.us_tax_rides.tax_rides_error",
                },
            }
        },
    )

    start_flex_template_job