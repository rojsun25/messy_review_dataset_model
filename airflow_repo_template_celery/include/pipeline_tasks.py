"""Reusable task functions for DAGs in this repo."""

from __future__ import annotations

import datetime as dt
import pandas as pd
from airflow.models import Variable


def extract() -> dict:
    now = dt.datetime.utcnow().isoformat()
    msg = Variable.get("example_message", default_var="hello")
    return {"extracted_at": now, "records": 3, "message": msg}


def transform(payload: dict) -> str:
    df = pd.DataFrame([payload])
    return df.to_json(orient="records")


def load(json_records: str) -> None:
    # Replace with your target sink (DB/S3/etc)
    print("Loaded:", json_records)
