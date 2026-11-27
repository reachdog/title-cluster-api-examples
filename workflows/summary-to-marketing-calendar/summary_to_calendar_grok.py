"""Turn a Reach Dog catalog summary into a 12-month marketing calendar, using Grok.

Grok first checks the audiences, occasions and seasons in the summary against your
own catalog and flags what doesn't hold up, then plans every month: a theme, the
products to feature, the audience, an email subject line and a social post idea.

Usage:
    python summary_to_calendar_grok.py --catalog my-catalog.csv --results reachdog-results.json
    python summary_to_calendar_grok.py --catalog my-catalog.csv --batch-id <your Reach Dog batch id>

Needs:
    pip install -r requirements-grok.txt
    XAI_API_KEY        (your xAI API key, from console.x.ai)
    TITLE_API_KEY      (your Reach Dog key, only with --batch-id to download the results)
Both are read from the environment, then from a .env file at the repo root.

The catalog CSV needs a "title" column (a price column helps Grok quote real prices).
The Reach Dog results must include the catalog_summary output.
"""
import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path

from openai import OpenAI  # the xAI API speaks the OpenAI format

HERE = Path(__file__).parent
REACHDOG_API = os.environ.get("TITLE_API_URL", "https://api.reach.dog").rstrip("/")
MODEL = os.environ.get("XAI_MODEL", "grok-4.7")
XAI_API = "https://api.x.ai/v1"
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def env_key(name: str) -> str:
    """Read a key from the environment, then from the .env file at the repo root."""
    value = os.environ.get(name, "").strip()
    if not value and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                value = line.split("=", 1)[1].strip()
    return value


def load_catalog(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "title" not in rows[0]:
        sys.exit(f"{path} needs a 'title' column.")
    return rows


def download_results(batch_id: str) -> dict:
    """Read the saved results of a finished Reach Dog catalog job (no extra charge)."""
    key = env_key("TITLE_API_KEY")
    if not key:
        sys.exit("Set TITLE_API_KEY to download results, or pass --results with a saved file.")
    outputs, cursor = {}, None
    while True:
        url = f"{REACHDOG_API}/v1/batches/{batch_id}/results?page_size=100"
        if cursor:
            url += f"&cursor={cursor}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
        page = json.load(urllib.request.urlopen(req))
        for name, value in page["outputs"].items():
            if isinstance(value, list) and isinstance(outputs.get(name), list):
                outputs[name] += value
            else:
                outputs[name] = value
        if not page.get("has_more"):
            return {"outputs": outputs}
        cursor = page["next_cursor"]


def load_results(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):  # a saved list of result pages
        data = data[0]
    return data if "outputs" in data else {"outputs": data}  # or just the outputs themselves


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", type=Path, required=True, help="your catalog CSV")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--results", type=Path, help="saved Reach Dog results JSON")
    src.add_argument("--batch-id", help="Reach Dog catalog job id to download")
    ap.add_argument("--out", type=Path, default=Path("marketing-calendar.md"))
    a = ap.parse_args()

    catalog = load_catalog(a.catalog)
    results = download_results(a.batch_id) if a.batch_id else load_results(a.results)
    outputs = results["outputs"]
    if "catalog_summary" not in outputs:
        sys.exit("The Reach Dog results don't include catalog_summary. Request that output.")
    summary = {"catalog_summary": outputs["catalog_summary"]}
    print(f"Catalog: {len(catalog)} products.")
    for field in ("top_demographics", "top_occasions", "top_seasons"):
        print(f"  {field[4:]:12s} {', '.join(summary['catalog_summary'].get(field, []))}")

    prompt = (HERE / "prompt.md").read_text(encoding="utf-8")
    catalog_csv = a.catalog.read_text(encoding="utf-8-sig")
    content = (
        f"<catalog_csv>\n{catalog_csv}\n</catalog_csv>\n\n"
        f"<reachdog_summary>\n{json.dumps(summary, indent=2)}\n</reachdog_summary>\n\n{prompt}"
    )

    print(f"\nSending to Grok ({MODEL}): check the summary, then plan the year...")
    grok_key = env_key("XAI_API_KEY")
    if not grok_key:
        sys.exit("Set XAI_API_KEY in your environment or in the .env file at the repo root.")
    client = OpenAI(api_key=grok_key, base_url=XAI_API, timeout=900)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
    )

    choice = response.choices[0]
    text = choice.message.content or ""
    if not text.strip():
        sys.exit("Grok returned an empty answer.")
    a.out.write_text(text, encoding="utf-8")
    usage = response.usage
    print(f"Done. Wrote {a.out} ({usage.prompt_tokens} in / {usage.completion_tokens} out tokens).")
    if choice.finish_reason == "length":
        print("Note: the answer hit the length limit and may be cut off.")


if __name__ == "__main__":
    main()
