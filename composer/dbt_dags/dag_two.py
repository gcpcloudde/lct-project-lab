from airflow import DAG
from airflow.models import Variable

from datetime import datetime
from common.constants import (
    IMAGE,
    COMMAND,
    REQUESTS_CONTAINER,
    LIMITS_CONTAINER,
    CONTAINER_ENV_VARS
)

from common.utils import create_kpo_with_full_pod_spec, reset_model_backfill_flag
from functools import partial
from common.alert_slack_channel import alert_slack_channel

slack_params = Variable.get("slack_env", deserialize_json=True)
ENV = Variable.get("env")
CHANNEL_ID = slack_params.get("PROD_CHANNEL_ID") if ENV == "prod" else slack_params.get("DEV_CHANNEL_ID")
SLACK_TOKEN = slack_params.get("SLACK_TOKEN")
USER_GROUP_ID = slack_params.get("PDT_SUPPORT_GROUP")

DAG_ID = "tbl_ocp_warehouse_shipping_order_dbt_dag"
POD_NAME = "tbl-ocp-warehouse-shipping-order-dbt"
TASK_NAME = "tbl_ocp_warehouse_shipping_order_dbt_dag"
INCREMENTAL_RUN = True
DAG_TAGS = ["returns"]
BASE_CONTAINER_NAME = "tbl-ocp-warehouse-shipping-order-dbt"
SCHEDULE_INTERVAL = "*/15 * * * *"  # Schedule to run every 15 mins
DBT_MODEL_BACKFILL_PARAMS = Variable.get("dbt_model_backfill_params", deserialize_json=True)
MODEL_NAME = "tbl_ocp_warehouse_shipment_order_pdt_stg"
try:
    full_refresh_flag = '--full-refresh' if DBT_MODEL_BACKFILL_PARAMS[MODEL_NAME] else ''
    backfill_flag = DBT_MODEL_BACKFILL_PARAMS[MODEL_NAME]
except KeyError:
    # Handle the case where MODEL_NAME is not present in DBT_MODEL_BACKFILL_PARAMS
    # Default Set to '' with the Dag creating a new key and set value to False
    full_refresh_flag = ''
    backfill_flag = None

run_id = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))//100
run_vars = {"run_id": run_id}
EXECUTE_COMMAND = f"dbt run {full_refresh_flag} --models {MODEL_NAME} --vars '{run_vars}'"

# Default settings applied to all tasks
#dbt run --models +tbl_carton_pdt_stg --vars '{ "run_id": 8989}' --target prod

default_args = {
    "catchup": False,
    "depends_on_past": False,
    "start_date": datetime(2024, 7, 21, 12, 00),
    "retries": 1,
    "concurrency": 1,
    "on_failure_callback": partial(alert_slack_channel, channel_id=CHANNEL_ID, slack_token=SLACK_TOKEN, user_group_id=USER_GROUP_ID)
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=False,
    max_active_runs=1,
    tags=DAG_TAGS,
) as dag:
    pod = create_kpo_with_full_pod_spec(
        POD_NAME,
        TASK_NAME,
        BASE_CONTAINER_NAME,
        IMAGE,
        COMMAND,
        EXECUTE_COMMAND,
        CONTAINER_ENV_VARS,
        REQUESTS_CONTAINER,
        LIMITS_CONTAINER,
    )

    if backfill_flag or backfill_flag is None:
        backfill_flag_reset = reset_model_backfill_flag(MODEL_NAME, DBT_MODEL_BACKFILL_PARAMS)
        pod >> backfill_flag_reset
