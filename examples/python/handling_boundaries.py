"""Reach Dog Title & Cluster API: handling uncertain and unavailable results.

A robust integration handles three cases beyond the happy path:
  1. A field with no value for this title: returned empty (null or []), not fabricated.
     This is a successful, billable answer.
  2. A parameter whose data source is not available yet: returned as an error with a
     clear code (for example unsupported_market), not a guess.
  3. A route your key is not scoped for (batch and catalog grouping): insufficient_scope.

Always branch on the error `code`, not on the HTTP status alone.

    pip install -r requirements.txt
    python handling_boundaries.py
"""
import os
import sys
import uuid
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


def post(path: str, payload: dict):
    resp = requests.post(
        f"{BASE_URL}{path}",
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
            "Idempotency-Key": uuid.uuid4().hex,
        },
        json=payload,
        timeout=120,
    )
    return resp.status_code, resp.json()


def describe(label: str, status: int, body: dict):
    if status < 400:
        # success: the field may be present but empty, which is meaningful
        key = next(iter(body), None)
        value = body.get(key)
        if value in (None, [], {}, ""):
            print(f"{label}: success, but empty ({key}={value!r}). Looked, found nothing.")
        else:
            print(f"{label}: success, has data ({key}).")
    else:
        print(f"{label}: {status} {body.get('code')} -> {body.get('message')}")


if __name__ == "__main__":
    # 1. Empty-but-successful fields
    describe("brand (none stated)", *post("/v1/title-matches",
             {"title": "4 person camping tent waterproof", "parameters": ["brand"]}))
    describe("compatibility (none stated)", *post("/v1/title-matches",
             {"title": "4 person camping tent waterproof", "parameters": ["compatibility"]}))

    # 2. A parameter whose source is not available yet
    describe("localized_terms (unavailable source)", *post("/v1/title-matches",
             {"title": "4 person camping tent waterproof", "parameters": ["localized_terms"],
              "locale": "es-ES", "market": "ES"}))

    # 3. A route your key is not scoped for
    describe("catalog-groups (out of scope)", *post("/v1/catalog-groups",
             {"batch_id": "example", "include": []}))
