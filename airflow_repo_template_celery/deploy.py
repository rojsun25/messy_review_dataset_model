#!/usr/bin/env python3
"""One-command deployment: `python deploy.py`

This repo is self-contained: Airflow config, Docker Compose, DAGs, and bootstrap data.

What this script does automatically:
1) Verifies Docker + Compose v2 is available
2) Creates required mount folders
3) Generates .env (AIRFLOW_UID + Airflow admin user/pass)
4) Builds the repo-owned Airflow image
5) Initializes Airflow DB and creates admin user (airflow-init)
6) Starts the full CeleryExecutor stack (scheduler, api-server, worker, triggerer, dag-processor, postgres, redis)
7) Imports Connections and Variables from ./bootstrap
8) Pauses/unpauses DAGs as configured in ./bootstrap/dags_state.json
9) Triggers a DAG run as configured in ./bootstrap/trigger.json
10) Polls the Airflow REST API until the DAG run completes (success/failure)

Prerequisites (cannot be installed reliably without admin rights):
- Docker Engine / Docker Desktop running
- docker compose v2

This is intended for dev/test.
"""

from __future__ import annotations

import base64
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = ROOT / "docker-compose.yaml"
ENV_FILE = ROOT / ".env"
BOOTSTRAP_DIR = ROOT / "bootstrap"

DEFAULT_USER = os.environ.get("AIRFLOW_ADMIN_USER", "airflow")
DEFAULT_PASS = os.environ.get("AIRFLOW_ADMIN_PASS", "airflow")

API_BASE = os.environ.get("AIRFLOW_API", "http://localhost:8080")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("
$", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True)


def ensure_tools() -> None:
    try:
        run(["docker", "version"], check=True)
    except Exception as e:
        raise SystemExit(
            "Docker is not available or not running. Install Docker Desktop/Engine and retry."
        ) from e

    try:
        run(["docker", "compose", "version"], check=True)
    except Exception as e:
        raise SystemExit(
            "docker compose (v2) is not available. Install Docker Compose v2 and retry."
        ) from e


def ensure_dirs() -> None:
    for d in ["dags", "logs", "plugins", "config", "include", "bootstrap"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)


def write_env() -> None:
    airflow_uid = "50000"
    if platform.system().lower() == "linux":
        try:
            airflow_uid = str(os.getuid())
        except Exception:
            airflow_uid = "50000"

    ENV_FILE.write_text(
        f"AIRFLOW_UID={airflow_uid}
"
        f"_AIRFLOW_WWW_USER_USERNAME={DEFAULT_USER}
"
        f"_AIRFLOW_WWW_USER_PASSWORD={DEFAULT_PASS}
"
    )
    print(f"Wrote {ENV_FILE}")


def compose(args: list[str], *, check: bool = True) -> None:
    run(["docker", "compose", "-f", str(COMPOSE_FILE)] + args, check=check)


def wait_for_health(timeout_s: int = 240) -> None:
    url = f"{API_BASE.rstrip('/')}/health"
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    print("Airflow API server is reachable:", url)
                    return
        except Exception:
            pass
        time.sleep(3)
    raise SystemExit("Airflow API server did not become healthy in time.")


def cli(*airflow_args: str, check: bool = True) -> None:
    # Use a one-off container to run airflow CLI in the same image/env.
    compose(["run", "--rm", "--no-deps", "airflow-scheduler", "airflow", *airflow_args], check=check)


def import_bootstrap() -> None:
    # Import connections (JSON array) and variables (JSON dict) if present
    conn_file = BOOTSTRAP_DIR / "connections.json"
    var_file = BOOTSTRAP_DIR / "variables.json"

    if conn_file.exists():
        cli("connections", "import", f"/opt/airflow/bootstrap/{conn_file.name}", check=True)
        print("Imported connections.")

    if var_file.exists():
        cli("variables", "import", f"/opt/airflow/bootstrap/{var_file.name}", check=True)
        print("Imported variables.")


def apply_dag_states() -> None:
    state_file = BOOTSTRAP_DIR / "dags_state.json"
    if not state_file.exists():
        return

    data = json.loads(state_file.read_text())
    for dag_id in data.get("pause", []):
        cli("dags", "pause", dag_id, check=False)
        print(f"Paused DAG: {dag_id}")

    for dag_id in data.get("unpause", []):
        cli("dags", "unpause", dag_id, check=False)
        print(f"Unpaused DAG: {dag_id}")


def _basic_auth_header(user: str, password: str) -> str:
    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def trigger_and_wait() -> None:
    trigger_file = BOOTSTRAP_DIR / "trigger.json"
    if not trigger_file.exists():
        print("No bootstrap/trigger.json found; skipping trigger.")
        return

    cfg = json.loads(trigger_file.read_text())
    dag_id = cfg["dag_id"]
    conf = cfg.get("conf", {})

    # Create a deterministic run_id for idempotence
    run_id = f"repo_deploy__{int(time.time())}"

    url = f"{API_BASE.rstrip('/')}/api/v1/dags/{dag_id}/dagRuns"
    payload = json.dumps({"dag_run_id": run_id, "conf": conf}).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", _basic_auth_header(DEFAULT_USER, DEFAULT_PASS))

    print(f"Triggering DAG '{dag_id}' with run_id '{run_id}'...")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            print("Trigger response:", body)
    except urllib.error.HTTPError as e:
        # If already exists, continue to polling
        print("Trigger HTTPError:", e.read().decode("utf-8"))

    # Poll run status
    status_url = f"{API_BASE.rstrip('/')}/api/v1/dags/{dag_id}/dagRuns/{run_id}"
    req2 = urllib.request.Request(status_url, method="GET")
    req2.add_header("Authorization", _basic_auth_header(DEFAULT_USER, DEFAULT_PASS))

    print("Waiting for DAG run completion...")
    timeout_s = int(os.environ.get("DAG_RUN_TIMEOUT_SECONDS", "3600"))
    start = time.time()

    while time.time() - start < timeout_s:
        try:
            with urllib.request.urlopen(req2, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
                state = (data.get("state") or "").lower()
                print(f"  state={state}  elapsed={int(time.time()-start)}s")

                if state in {"success"}:
                    print("DAG run SUCCEEDED.")
                    return
                if state in {"failed"}:
                    raise SystemExit("DAG run FAILED.")
        except urllib.error.HTTPError as e:
            print("Poll error:", e.read().decode("utf-8"))
        except Exception as e:
            print("Poll exception:", e)

        time.sleep(10)

    raise SystemExit("Timed out waiting for DAG run completion.")


def main() -> None:
    ensure_tools()
    ensure_dirs()
    write_env()

    # Build image & init DB/admin
    compose(["up", "--build", "airflow-init"], check=True)

    # Start the stack
    compose(["up", "-d", "--build"], check=True)

    wait_for_health()

    # Bootstrap metadata
    import_bootstrap()
    apply_dag_states()

    # Trigger and wait end-to-end
    trigger_and_wait()

    print("
Done.")
    print(f"Airflow UI/API: {API_BASE}")
    print(f"Login: {DEFAULT_USER} / {DEFAULT_PASS}")
    print("Stop: docker compose down")


if __name__ == "__main__":
    main()
