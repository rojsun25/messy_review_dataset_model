# Airflow-in-Repo (CeleryExecutor) — one command deploy

This repository is **fully self-contained** for running Apache Airflow locally using **Docker Compose** with **CeleryExecutor** (Redis broker + Postgres metadata DB).

## What you run

```bash
python3 deploy.py
```

That single command will:
- Build the repo-owned Airflow image (installs `requirements.txt`)
- Initialize Airflow metadata DB + create an admin user
- Start the full Airflow stack
- Import **Connections** and **Variables** from `./bootstrap`
- Pause/unpause DAGs per `./bootstrap/dags_state.json`
- Trigger a DAG run per `./bootstrap/trigger.json`
- Wait until the DAG run completes (success/failure)

## Prerequisites
- Docker Engine / Docker Desktop is installed and running
- `docker compose` (Compose v2)

## URLs
- Airflow UI/API: http://localhost:8080
- Flower (optional): http://localhost:5555 (start with `docker compose --profile flower up -d`)

## Bootstrap files
- `bootstrap/connections.json`  (Airflow connections import format)
- `bootstrap/variables.json`    (Airflow variables import format)
- `bootstrap/dags_state.json`   (`pause`/`unpause` lists)
- `bootstrap/trigger.json`      (`dag_id` and optional `conf`)

## Admin credentials
Default: `airflow / airflow`

Override without editing files:

```bash
AIRFLOW_ADMIN_USER=admin AIRFLOW_ADMIN_PASS=admin123 python3 deploy.py
```

## Tear down
Stop containers (keep DB volume):

```bash
docker compose down
```

Destroy containers + volumes (reset DB):

```bash
python3 destroy.py
```
