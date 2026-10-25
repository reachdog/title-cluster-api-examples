# Reach Dog Product Classification API: Examples

Turn a product title into structured product data: product type, attributes, categories, buyer language, keyword demand, market research, and marketing content. You ask for the exact fields you want and get back only those.

This repository holds working, runnable examples for integrating the Reach Dog Title and Cluster API. The service implementation is private; everything here is client-side example code you can run against the live API with your own key.

- Live demo: https://huggingface.co/spaces/ReachDog/product-classification-api-demo
- Get a key: https://platform.reach.dog/keys
- Developer reference: [docs/api-reference.md](docs/api-reference.md)
- Changelog: [docs/changelog.md](docs/changelog.md)
- API reference (OpenAPI): https://title-cluster-api-221381283627.us-east1.run.app/openapi.json

## What can I build with this?

Anything that needs clean structured data from a messy product title, without manual tagging:

- Catalog enrichment and PIM pipelines (product type, attributes, categories)
- On-site search and merchandising (synonyms, facets, collections, related products)
- SEO and paid-search planning (real buyer keywords with volume, cost, and competition)
- Market and competitive research (how big a segment is, which brands and sellers are present)
- Grounded marketing content (ad, blog, and video topics, briefs, and drafts)

## What do I send?

A product title and a list of the parameters you want back. Each parameter is requested by name or by numeric id.

```json
{
  "title": "4 person camping tent waterproof",
  "parameters": ["product_type", "attributes", "synonyms"]
}
```

## What comes back?

Exactly the parameters you asked for, as flat top-level fields, and nothing else. This is a real response from the call above:

```json
{
  "product_type": "camping tent",
  "attributes": [
    { "name": "Capacity", "value": "4 person" },
    { "name": "Waterproof", "value": "waterproof" }
  ],
  "synonyms": ["camping tent", "tent"]
}
```

Keyword parameters come back as records with their own ids and measurements. A request for `["search_volume"]` returns:

```json
{
  "search_volume": [
    { "id": "13654206", "text": "Outdoor waterproof tents", "search_volume": 260 },
    { "id": "13654207", "text": "Tents for heavy rain", "search_volume": 20 },
    { "id": "5639376", "text": "Best tents for bad weather?", "search_volume": 30 },
    { "id": "13654203", "text": "Top waterproof tents for backpacking", "search_volume": null }
  ]
}
```

A `null` value means that specific measurement was not available for that record. The API reports absence honestly rather than inventing a number.

## How do I run the example?

1. Copy `.env.example` to `.env` and set your key:
   ```
   TITLE_API_KEY=your_key_here
   ```
2. Python:
   ```bash
   cd examples/python
   pip install -r requirements.txt
   python quickstart.py
   ```
3. JavaScript (Node 18 or newer):
   ```bash
   cd examples/javascript
   node quickstart.js
   ```

Both read `TITLE_API_KEY` from the environment. Never hardcode a key or commit it.

## Handling uncertain and unavailable results

Good integrations handle the boundaries, not just the happy path. These are all real API responses.

**A field with no value for this title comes back empty, not fabricated.** A title with no stated brand returns `null`; a request for `compatibility` on a product that states none returns an empty list:

```json
{ "brand": null }
{ "compatibility": [] }
```

An empty result is a successful, billable answer. It means the API looked and there was nothing to return, which is useful information.

**Some parameters depend on data sources that are not available yet.** They return a clear error instead of a guess. For example, localized terms are not supported today:

```json
{ "code": "unsupported_market", "message": "Title taxonomy sources do not support a market filter.", "retryable": false }
```

**Funded wallet accounts can use catalog grouping through `POST /v1/batches`
with `workflow: "catalog_local_v1"`.** Submission requires a bound shared wallet
and `match` or `batch` scope; saved status/results require `read`. The existing
catalog flow returns a quote, starts only after acceptance, and provides paged
results. See [the catalog workflow](https://platform.reach.dog/docs/catalog-workflow).
This does not open the unrelated legacy title-batch or `/v1/catalog-groups` routes.

Error envelopes always carry a `code`, a `message`, a `request_id`, and a `retryable` flag. Read `code`, not the HTTP status alone.

## How do I get access, and what does it cost?

1. Open https://platform.reach.dog/keys, sign in using the console's available options, and follow the wallet/key setup for your account.
2. Send it as `Authorization: Bearer <key>` and include an `Idempotency-Key` header on each request.
3. Single-title pricing is per requested parameter, billed when the request succeeds, with no base fee. Read `parameter_price` from `GET /v1/usage` for your current unit price. A correct empty result still counts as a success; failed requests are not billed. Catalog outputs are priced per selected output per catalog call, not per title; inspect its returned quote.
4. Do not assume a universal free allowance. GitHub sign-in provides the console's eligible API/recipe evaluation path; Google/email console testing requires purchased wallet credits. Direct API-key requests follow the key's scopes, account access and wallet balance. Check `GET /v1/usage` and the console for your account's current balance and limits. Wallet credits are Reach Dog billing units, not model tokens.

Repeating the same request with the same `Idempotency-Key` returns the saved answer with no new charge, within the idempotency window.

## Parameters

You can request any mix of parameters in one call. A readable grouping of the parameters by job (product understanding, buyer language, keyword demand, merchandising, market research, occasion insights, content generation) is in the parameter packages guide. The full machine-readable list is in the OpenAPI document linked at the top.

## Tutorials

- [Extract structured attributes from product titles](docs/extract-attributes-from-product-titles.md)

## Suggested repository metadata (for maintainers)

- Description: `Working examples for the Reach Dog Product Classification API: turn product titles into structured product data, keywords, and market research.`
- Topics: `ecommerce`, `product-classification`, `product-taxonomy`, `attribute-extraction`, `product-enrichment`, `keyword-research`, `api`, `python`, `javascript`

## Support

Open an issue in this repository for example-code problems. For API access and billing, use the developer access page.
