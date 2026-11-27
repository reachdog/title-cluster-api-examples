# Catalog summary to a 12-month marketing calendar, with Claude

Reach Dog reads your whole catalog and sums it up: the top categories, who your products are for, the occasions and use cases they fit, and the seasons they sell in. This workflow hands that summary to Claude, which checks it against your own products first, then plans a full year of marketing.

## What you need

- Your catalog as a CSV with a `title` column. A price column helps Claude use real prices in the copy.
- A Reach Dog catalog job with the `catalog_summary` output. See the [catalog workflow](https://platform.reach.dog/docs/catalog-workflow) and https://reach.dog/developers/catalog-enrichment-api
- A Claude account (for the chat version) or a Claude API key (for the script).

## In the Claude app

1. Attach your catalog CSV and the Reach Dog summary JSON.
2. Paste the prompt from [prompt.md](prompt.md).

## Optional: audit the Reach Dog JSON first

In a fresh chat, attach the same two files and paste the prompt from [../audit-prompt.md](../audit-prompt.md). Your model reviews the JSON against your catalog and suggests improvements before you start.

## With the script

Put `ANTHROPIC_API_KEY` and `TITLE_API_KEY` in the `.env` file at the repo root (see `.env.example`), then:

```
cd workflows/summary-to-marketing-calendar
pip install -r requirements.txt
python summary_to_calendar.py --catalog my-catalog.csv --batch-id <your Reach Dog catalog job id>
```

Or pass a saved results file with `--results reachdog-results.json`. The script writes `marketing-calendar.md`.

## What you get

1. A check of the summary: for every audience, occasion and season, the products that back it up, with the weak ones flagged (too generic, only one product, or a guess). It also points out labels that go further than your product titles, and seasons the summary leaves out.
2. A 12-month calendar: a theme, the audience and the products to feature for each month, with the quiet months marked.
3. One email subject line and one social post idea per month, built from your real products.
4. A coverage check, so every product is featured at least once.

Anything Claude would need from you, such as your sale dates or shipping cutoffs, comes back in [brackets]. Review the calendar before you use it.

## Try it on the demo

The `workflows/demo` folder has a made-up 20-product candle shop and its real Reach Dog catalog summary:

```
python summary_to_calendar.py --catalog ../demo/demo-catalog-hearth-and-wick.csv --results ../demo/reachdog-catalog-summary.json
```
