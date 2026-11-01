from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2)
}
with DAG(
    dag_id="churn_daily_pipeline",
    description="Daily customer churn prediction pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["churn", "ml", "dbt"],

) as dag:
    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command="python ml/load.py",
        cwd="/opt/airflow",
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "dbt run "
            "--project-dir /opt/airflow/dbt_project "
            "--profiles-dir /home/airflow/.dbt"
        ),
        cwd="/opt/airflow",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "dbt test "
            "--project-dir /opt/airflow/dbt_project "
            "--profiles-dir /home/airflow/.dbt"
        ),
        cwd="/opt/airflow",
    )

    predict = BashOperator(
        task_id="predict_churn",    
        bash_command="python ml/predict.py",
        cwd="/opt/airflow",
    )

    load_raw_data >> dbt_run >> dbt_test >> predict