"""Reach Dog Title & Cluster API: keyword demand example.

Requests real keyword metrics for a product title: search volume, cost per click,
and the paid-search competition label. Each keyword comes back as a record with its
own id. Some measurements may be null when the data is not available for that record.

    pip install -r requirements.txt
    python keyword_demand.py
"""
import os
import sys
import uuid
import json
from pathlib import Path

import requests

BASE_URL = os.environ.get(
    "TITLE_API_URL", "https://title-cluster-api-221381283627.us-east1.run.app"
).rstrip("/")


def load_key() -> str:
    key = os.environ.get("TITLE_API_KEY", "").strip()
    if key:
        return key
    env = Path(__file__).resolve().parents[2] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("TITLE_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("Set TITLE_API_KEY in your environment or in a .env file at the repo root.")


def ask(title: str, parameters: list) -> dict:
    resp = requests.post(
        f"{BASE_URL}/v1/title-matches",
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
            "Idempotency-Key": uuid.uuid4().hex,
        },
        json={"title": title, "parameters": parameters},
        timeout=120,
    )
    body = resp.json()
    if resp.status_code >= 400:
        code = body.get("code", "error")
        raise RuntimeError(f"{resp.status_code} {code}: {body.get('message')} (request_id={body.get('request_id')})")
    return body


if __name__ == "__main__":
    result = ask(
        "4 person camping tent waterproof",
        ["search_volume", "cpc", "paid_search_competition"],
    )
    for row in result.get("search_volume", []):
        volume = row.get("search_volume")
        shown = volume if volume is not None else "not available"
        print(f"{row['text']!r}: volume={shown} (keyword id {row['id']})")
    print()
    print(json.dumps(result, indent=2))
