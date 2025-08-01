from airflow import DAG
from airflow.models import Variable
from datetime import datetime
from functools import partial
from common.constants import (
    IMAGE, COMMAND, REQUESTS_CONTAINER, LIMITS_CONTAINER, CONTAINER_ENV_VARS
)
from common.utils import create_kpo_with_full_pod_spec, reset_model_backfill_flag
from common.alert_slack_channel import alert_slack_channel

# Slack + Airflow defaults
slack_params = Variable.get("slack_env", deserialize_json=True)
ENV = Variable.get("env")
CHANNEL_ID = slack_params.get("PROD_CHANNEL_ID") if ENV == "prod" else slack_params.get("DEV_CHANNEL_ID")
SLACK_TOKEN = slack_params.get("SLACK_TOKEN")
USER_GROUP_ID = slack_params.get("PDT_SUPPORT_GROUP")
DBT_MODEL_BACKFILL_PARAMS = Variable.get("dbt_model_backfill_params", deserialize_json=True)

default_args = {
    "catchup": False,
    "depends_on_past": False,
    "start_date": datetime(2024, 7, 21, 12, 0),
    "retries": 1,
    "concurrency": 1,
    "on_failure_callback": partial(
        alert_slack_channel,
        channel_id=CHANNEL_ID,
        slack_token=SLACK_TOKEN,
        user_group_id=USER_GROUP_ID
    ),
}

# Define shared DAG
with DAG(
    dag_id="advice_and_order_dag",
    default_args=default_args,
    schedule_interval="*/60 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["returns","warehouse","advice","order"],
) as dag:

    # Define task-specific parameters using dictionaries
    task_configs = [
        {
            "task_name": "tbl_ocp_warehouse_shipping_advice_dbt_dag",
            "pod_name": "tbl-ocp-warehouse-shipping-advice-dbt",
            "base_container_name": "tbl-ocp-warehouse-shipping-advice-dbt",
            "model_name": "tbl_ocp_warehouse_shipment_advice_pdt_stg"
        },
        {
            "task_name": "tbl_ocp_warehouse_shipping_order_dbt_dag",
            "pod_name": "tbl-ocp-warehouse-shipping-order-dbt",
            "base_container_name": "tbl-ocp-warehouse-shipping-order-dbt",
            "model_name": "tbl_ocp_warehouse_shipment_order_pdt_stg"
        }
    ]

    # Store task references for potential downstream chaining
    task_refs = []

    for config in task_configs:
        model_name = config["model_name"]

        try:
            full_refresh_flag = '--full-refresh' if DBT_MODEL_BACKFILL_PARAMS[model_name] else ''
            backfill_flag = DBT_MODEL_BACKFILL_PARAMS[model_name]
        except KeyError:
            full_refresh_flag = ''
            backfill_flag = None

        run_id = int(datetime.now().strftime("%Y%m%d%H%M%S%f")) // 100
        run_vars = {"run_id": run_id}
        EXECUTE_COMMAND = f"dbt run {full_refresh_flag} --models {model_name} --vars '{run_vars}'"

        pod = create_kpo_with_full_pod_spec(
            pod_name=config["pod_name"],
            task_name=config["task_name"],
            base_container_name=config["base_container_name"],
            image=IMAGE,
            command=COMMAND,
            execute_command=EXECUTE_COMMAND,
            container_env_vars=CONTAINER_ENV_VARS,
            requests_container=REQUESTS_CONTAINER,
            limits_container=LIMITS_CONTAINER,
        )

        if backfill_flag or backfill_flag is None:
            reset_flag = reset_model_backfill_flag(model_name, DBT_MODEL_BACKFILL_PARAMS)
            pod >> reset_flag
            task_refs.append(pod)
        else:
            task_refs.append(pod)
