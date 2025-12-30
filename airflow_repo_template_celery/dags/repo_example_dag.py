from __future__ import annotations

import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator

from include.pipeline_tasks import extract, transform, load


with DAG(
    dag_id="repo_example_dag",
    description="Example DAG shipped with the repo (CeleryExecutor stack).",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["repo", "example"],
) as dag:

    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform, op_args=[t_extract.output])
    t_load = PythonOperator(task_id="load", python_callable=load, op_args=[t_transform.output])

    t_extract >> t_transform >> t_load
