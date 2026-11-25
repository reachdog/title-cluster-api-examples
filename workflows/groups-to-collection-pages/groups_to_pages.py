"""Turn Reach Dog catalog groups into collection pages with breadcrumbs, using Claude.

Claude first checks every group Reach Dog built against your own product titles,
then writes a collection page and a breadcrumb for each group.

Usage:
    python groups_to_pages.py --catalog my-catalog.csv --results reachdog-results.json
    python groups_to_pages.py --catalog my-catalog.csv --batch-id <your Reach Dog batch id>

Needs:
    pip install -r requirements.txt
    ANTHROPIC_API_KEY  (your Claude API key)
    TITLE_API_KEY      (your Reach Dog key, only with --batch-id to download the results)
Both are read from the environment, then from a .env file at the repo root.

The catalog CSV needs a "title" column. The Reach Dog results must include the
catalog_groups and group_members outputs.
"""
import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path

import anthropic

HERE = Path(__file__).parent
REACHDOG_API = os.environ.get("TITLE_API_URL", "https://api.reach.dog").rstrip("/")
MODEL = "claude-opus-5-5"
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
    ap.add_argument("--out", type=Path, default=Path("collection-pages.md"))
    a = ap.parse_args()

    catalog = load_catalog(a.catalog)
    results = download_results(a.batch_id) if a.batch_id else load_results(a.results)
    outputs = results["outputs"]
    missing = [k for k in ("catalog_groups", "group_members") if k not in outputs]
    if missing:
        sys.exit(f"The Reach Dog results don't include {', '.join(missing)}. Request those outputs.")
    groups = {"catalog_groups": outputs["catalog_groups"], "group_members": outputs["group_members"]}

    print(f"Catalog: {len(catalog)} products. Reach Dog groups: {len(groups['catalog_groups'])}.")
    for g in groups["catalog_groups"]:
        print(f"  {g['family']:10s} {g['label']} ({g['count']})")

    prompt = (HERE / "prompt.md").read_text(encoding="utf-8")
    catalog_csv = a.catalog.read_text(encoding="utf-8-sig")
    content = (
        f"<catalog_csv>\n{catalog_csv}\n</catalog_csv>\n\n"
        f"<reachdog_groups>\n{json.dumps(groups, indent=2)}\n</reachdog_groups>\n\n{prompt}"
    )

    print(f"\nSending to Claude ({MODEL}): check the groups, then write the pages...")
    claude_key = env_key("ANTHROPIC_API_KEY")
    if not claude_key:
        sys.exit("Set ANTHROPIC_API_KEY in your environment or in the .env file at the repo root.")
    client = anthropic.Anthropic(api_key=claude_key)
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # if this model declines, the API retries on a fallback model
        messages=[{"role": "user", "content": content}],
    ) as stream:
        response = stream.get_final_message()

    if response.stop_reason == "refusal":
        sys.exit("Claude declined this request.")
    text = "".join(b.text for b in response.content if b.type == "text")
    a.out.write_text(text, encoding="utf-8")
    print(f"Done. Wrote {a.out} ({response.usage.input_tokens} in / {response.usage.output_tokens} out tokens).")
    if response.stop_reason == "max_tokens":
        print("Note: the answer hit the length limit and may be cut off.")


if __name__ == "__main__":
    main()
