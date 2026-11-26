# Catalog groups to collection pages, with Claude

Reach Dog sorts your catalog into groups by season, occasion and use. This workflow hands those groups to Claude, which checks every group against your own product titles and then writes a collection page and a breadcrumb for each group.

## What you need

- Your catalog as a CSV with a `title` column.
- A Reach Dog catalog job with the `catalog_groups` and `group_members` outputs. See the [catalog workflow](https://platform.reach.dog/docs/catalog-workflow) and https://reach.dog/developers/catalog-enrichment-api
- A Claude account (for the chat version) or a Claude API key (for the script).

## In the Claude app

1. Attach your catalog CSV and the Reach Dog groups JSON.
2. Paste the prompt from [prompt.md](prompt.md).

## Optional: audit the Reach Dog JSON first

In a fresh chat, attach the same two files and paste the prompt from [../audit-prompt.md](../audit-prompt.md). Your model reviews the JSON against your catalog and suggests improvements before you start.

## With the script

Put `ANTHROPIC_API_KEY` and `TITLE_API_KEY` in the `.env` file at the repo root (see `.env.example`), then:

```
cd workflows/groups-to-collection-pages
pip install -r requirements.txt
python groups_to_pages.py --catalog my-catalog.csv --batch-id <your Reach Dog catalog job id>
```

Or pass a saved results file with `--results reachdog-results.json`. The script writes `collection-pages.md`.

## With Grok

The same prompt works in the Grok app (grok.com): attach your catalog CSV and the Reach Dog JSON, then paste `prompt.md`. The audit prompt works there too.

To run it from code with the xAI API, put `XAI_API_KEY` and `TITLE_API_KEY` in the `.env` file at the repo root, then:

```
cd workflows/groups-to-collection-pages
pip install -r requirements-grok.txt
python groups_to_pages_grok.py --catalog my-catalog.csv --batch-id <your Reach Dog catalog job id>
```

It sends the same prompt to `grok-4.7` by default. Set `XAI_MODEL` to use another Grok model.

## What you get

1. A check table per group: every product marked keep or question, with a one-line reason, plus products that look like they belong but are missing.
2. A collection page per group, built only from the kept products: H1, meta description, short intro, product list.
3. A breadcrumb per page (Home > Shop by Season > Winter, and so on) as HTML and as schema.org BreadcrumbList JSON-LD.

Anything Claude would need from you, such as scent notes, materials or your store name, comes back in [brackets]. Review the pages before you publish them.

## Try it on the demo

The `workflows/demo` folder has a made-up 20-product candle shop and its real Reach Dog groups:

```
python groups_to_pages.py --catalog ../demo/demo-catalog-hearth-and-wick.csv --results ../demo/reachdog-catalog-groups.json
```
