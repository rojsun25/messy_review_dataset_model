# Repo-owned Airflow image (CeleryExecutor) with DAG dependencies baked in.
FROM apache/airflow:3.1.5

USER root
# Add OS packages here if needed
# RUN apt-get update && apt-get install -y --no-install-recommends <pkgs> #  && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
