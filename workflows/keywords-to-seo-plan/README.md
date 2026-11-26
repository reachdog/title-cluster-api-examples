# Keyword opportunities to an SEO keyword plan, with Claude

Reach Dog finds the real searches behind your catalog: the search term, monthly searches, a category and how competitive each one is. This workflow hands that list to Claude, which checks every keyword against your own products before it uses any of them, then builds a keyword plan for your product pages.

## What you need

- Your catalog as a CSV with a `title` column.
- A Reach Dog catalog job with the `catalog_keyword_opportunities` output. See the [catalog workflow](https://platform.reach.dog/docs/catalog-workflow) and https://reach.dog/developers/catalog-enrichment-api
- A Claude account (for the chat version) or a Claude API key (for the script).

## In the Claude app

1. Attach your catalog CSV and the Reach Dog keywords JSON.
2. Paste the prompt from [prompt.md](prompt.md).

The prompt was written for the demo candle shop. Change the drop rules to fit yours: "making candles yourself" becomes whatever the do-it-yourself version of your products is.

## Optional: audit the Reach Dog JSON first

In a fresh chat, attach the same two files and paste the prompt from [../audit-prompt.md](../audit-prompt.md). Your model reviews the JSON against your catalog and suggests improvements before you start.

## With the script

Put `ANTHROPIC_API_KEY` and `TITLE_API_KEY` in the `.env` file at the repo root (see `.env.example`), then:

```
cd workflows/keywords-to-seo-plan
pip install -r requirements.txt
python keywords_to_seo_plan.py --catalog my-catalog.csv --batch-id <your Reach Dog catalog job id>
```

Or pass a saved results file with `--results reachdog-results.json`. The script writes `seo-keyword-plan.md`.

## With Grok

The same prompt works in the Grok app (grok.com): attach your catalog CSV and the Reach Dog JSON, then paste `prompt.md`. The audit prompt works there too.

To run it from code with the xAI API, put `XAI_API_KEY` and `TITLE_API_KEY` in the `.env` file at the repo root, then:

```
cd workflows/keywords-to-seo-plan
pip install -r requirements-grok.txt
python keywords_to_seo_plan_grok.py --catalog my-catalog.csv --batch-id <your Reach Dog catalog job id>
```

It sends the same prompt to `grok-4.7` by default. Set `XAI_MODEL` to use another Grok model.

## What you get

1. A screening table: the keywords Claude dropped, in groups (other brands, do-it-yourself, bulk and wholesale, things you don't sell), with a reason for each group. Duplicates are merged.
2. A keyword table: one main keyword and up to two supporting keywords per product, with monthly searches. Each keyword goes to only one product, so your own pages don't compete with each other.
3. An SEO title (under 60 characters) and meta description (under 155) per product.
4. The products with no good keyword, flagged.
5. FAQ and blog topics from the question keywords, each with the product it should link to. Safety and health questions are set aside, not answered.

Anything Claude would need from you, such as burn times or materials, comes back in [brackets]. Review the plan before you publish anything.

## Try it on the demo

The `workflows/demo` folder has a made-up 20-product candle shop and its real Reach Dog keyword opportunities:

```
python keywords_to_seo_plan.py --catalog ../demo/demo-catalog-hearth-and-wick.csv --results ../demo/reachdog-keyword-opportunities.json
```
