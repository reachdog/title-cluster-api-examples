"""Reach Dog Title & Cluster API: Python quickstart.

Sends a product title and asks for three parameters, then prints the response.
Reads the key from the TITLE_API_KEY environment variable (or a .env file at the
repo root). Never hardcode your key.

    pip install -r requirements.txt
    python quickstart.py
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
    # fall back to a .env file at the repo root (two levels up)
    env = Path(__file__).resolve().parents[2] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("TITLE_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("Set TITLE_API_KEY in your environment or in a .env file at the repo root.")


def ask(title: str, parameters: list) -> dict:
    """Request parameters for a product title. Returns the parsed JSON response."""
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
        # Error envelopes carry code / message / request_id / retryable.
        code = body.get("code", "error")
        raise RuntimeError(f"{resp.status_code} {code}: {body.get('message')} (request_id={body.get('request_id')})")
    return body


if __name__ == "__main__":
    result = ask(
        "4 person camping tent waterproof",
        ["product_type", "attributes", "synonyms"],
    )
    print(json.dumps(result, indent=2))
