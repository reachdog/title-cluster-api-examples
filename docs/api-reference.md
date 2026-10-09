# Reach Dog Title and Cluster API: developer reference

The API turns an e-commerce product title into structured product data. You send a title and the exact parameters you want back, and the response holds only those parameters. The same request shape also powers market research on a product type or brand, and marketing-content generation from a saved result.

This page is the full reference. If you just want to make a first call, start with the [README](../README.md) and the [attribute walkthrough](extract-attributes-from-product-titles.md).

- Base URL: `https://title-cluster-api-221381283627.us-east1.run.app`
- Current contract: OpenAPI `0.2.0`, schema `2026-09-30.4` (see [Versioning](#versioning))
- Get a key: https://intersect.reach.dog/developer

## Contents

1. [Authentication](#authentication)
2. [Pricing and the free tier](#pricing-and-the-free-tier)
3. [Request basics](#request-basics)
4. [Endpoints](#endpoints)
5. [Parameters](#parameters)
6. [Response model](#response-model)
7. [Errors](#errors)
8. [Idempotency and saved results](#idempotency-and-saved-results)
9. [Performance](#performance)
10. [Versioning](#versioning)

## Authentication

Every request needs a bearer key:

```
Authorization: Bearer <your_key>
```

Create a key at https://intersect.reach.dog/developer by signing in with Google. A new key can call the title, research and content endpoints. Batch and catalog-grouping are not part of the developer offering (see [Endpoints](#endpoints)). Keep keys out of source control and client-side code.

A missing or invalid key returns `401 invalid_key`.

## Pricing and the free tier

- You pay per requested parameter. At current pricing each parameter costs **25 tokens**, so a three-parameter request costs 75 tokens. There is no base fee.
- Billing is success only. A correct answer with an empty value (`null` or `[]`) still counts as a success and is billed. A failed request (validation error, an unavailable source, a dependency failure) is not billed.
- Every account has a **free daily allowance of about 10,000 tokens** (roughly 400 single-parameter calls at current pricing), refreshed every 24 hours. You can evaluate the whole API without adding funds.
- Check your balance and limits any time with [`GET /v1/usage`](#get-v1usage). Pricing and the allowance can change, so treat `/v1/usage` and the access page as the source of truth, not this number.

## Request basics

- Content type is `application/json`.
- Creation requests (`POST`) require an `Idempotency-Key` header. See [Idempotency](#idempotency-and-saved-results).
- `parameters` is a list of 1 to 68 entries. Each entry is a parameter name (`"product_type"`) or its register id (`2`). Names and ids may be mixed; they normalize to register order.
- Selecting the same parameter twice, including once by id and once by name, is rejected rather than billed twice.
- Unknown names, parameters that do not belong to the endpoint, and an empty list are rejected with `422`.

## Endpoints

| Method and path | Purpose |
|---|---|
| `POST /v1/title-matches` | Analyze one product title. Returns the requested title, discovery and merchandising parameters. |
| `GET /v1/title-matches/{id}` | Fetch a saved title result. No new work, no charge. |
| `POST /v1/market-research` | Research a typed subject (product type, category, brand, dimension, or an owned result). Returns the requested research parameters. |
| `GET /v1/market-research/{id}` | Fetch a saved research result. |
| `POST /v1/content-generations` | Generate marketing content from a saved, owned result. Returns the requested content parameters. |
| `GET /v1/content-generations/{id}` | Fetch a saved content result. |
| `GET /v1/usage` | Your balance, price, daily limit and refill time. |
| `GET /v1/versions` | Dataset, schema and matcher versions. |

Batch (`/v1/batches`) and catalog grouping (`/v1/catalog-groups`) exist in the API but are not available to developer keys. They answer `403 insufficient_scope`. Do not build against them.

### POST /v1/title-matches

Body fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | Up to 1000 characters. |
| `parameters` | array | yes | 1 to 68 names or ids. |
| `client_product_id` | string | no | Your own id for the product. Needed by `keyword_product_matches`. |
| `description` | string | no | Up to 10000 characters. |
| `attributes` | object | no | Known attribute values you already have. |
| `locale`, `market` | string | no | Reserved. The title taxonomy is English only today, so `market` is rejected for `localized_terms`. |

Request:

```json
{
  "title": "4 person camping tent waterproof",
  "parameters": ["product_type", "attributes", "synonyms"]
}
```

Response (a real result, trimmed):

```json
{
  "product_type": "camping tent",
  "attributes": [
    { "name": "Capacity", "value": "4 person" },
    { "name": "Waterproof", "value": "waterproof" }
  ],
  "synonyms": ["4 person waterproof tent"]
}
```

### POST /v1/market-research

Body fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `subject` | object | yes | A typed subject (below). |
| `parameters` | array | yes | Research parameters only. |
| `market`, `locale` | string | no | Reserved. |

The `subject` object has a `type` from `product_type`, `category`, `brand`, `dimension`, `title_result`, `catalog_group`, with the matching field: `value` for product_type, category and brand; `dimension` plus `value` for a dimension; `id` for an owned `title_result`; `grouping_id` or `group_id` for an owned grouping. A valid subject shape does not guarantee every parameter supports it; unsupported combinations return `422 unsupported_subject_selection`.

Request:

```json
{
  "subject": { "type": "product_type", "value": "camping tent" },
  "parameters": ["market_coverage", "brand_presence"]
}
```

Response (real, trimmed):

```json
{
  "market_coverage": { "products": 314, "merchants": 135, "brands": 55 },
  "brand_presence": [
    { "name": "coleman", "products": 53, "product_share": 0.16879, "observed_at": "2026-07-16T22:05:27" }
  ]
}
```

### POST /v1/content-generations

Content is generated from a result you already own, not from a bare title. Create a `title_result` first with `POST /v1/title-matches`, then pass its id as the content source.

Body fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `source` | object | yes | `{ "subject": { "type": "title_result", "id": "<saved id>" }, "objective": "...", "brand_voice": "..." }`. `objective` and `brand_voice` are optional. |
| `parameters` | array | yes | Content parameters only. |
| `channels` | array | yes | 1 to 10 of `blog`, `sem`, `email`, `product`, `instagram`, `facebook`, `x`, `pinterest`, `tiktok`, `youtube`. `ad_topics` needs `sem`, `blog_topics` needs `blog`, `video_topics` needs a video channel. |

Request:

```json
{
  "source": {
    "subject": { "type": "title_result", "id": "example_title_result" },
    "objective": "Explain how to choose a 4-person waterproof camping tent"
  },
  "parameters": ["blog_topics", "content_brief"],
  "channels": ["blog"]
}
```

Content is never published, and it does not invent prices, specifications or performance claims. `keyword_content_groups` needs a source that was created with keyword parameters, otherwise it returns `422 keywords_required`.

### GET /v1/usage

```json
{
  "day_utc": "2026-10-09",
  "wallet_balance": 10000,
  "parameter_price": 25,
  "daily_title_limit": 10000,
  "api_limit_resets_at": "2026-10-10T00:00:00+00:00",
  "wallet_refill_eligible_at": "2026-10-10T17:27:45+00:00",
  "billing": "shared_wallet"
}
```

### GET /v1/versions

```json
{
  "dataset_version": "registry-2026-07-21",
  "schema_version": "2026-09-30.4",
  "matcher_version": "catalog-matching-v0.2.0"
}
```

## Parameters

Request any mix of parameters in one call. Each belongs to one endpoint family. The table marks availability: **live** works today, **source pending** returns `503 source_unavailable` until its data source ships, and **not for dev keys** is blocked for developer keys.

### Title: product understanding

| id | name | availability |
|---:|---|---|
| 1 | `title` | live |
| 2 | `product_type` | live |
| 3 | `brand` | live (null when the title states none) |
| 4 | `attributes` | live |
| 5 | `categories` | live |
| 6 | `use_cases` | live |
| 7 | `occasions` | live |
| 8 | `audiences` | live |
| 9 | `seasons` | live |
| 10 | `where` | live |
| 11 | `why` | live |
| 12 | `how` | live |
| 17 | `synonyms` | live |

### Title: discovery (buyer language)

| id | name | availability |
|---:|---|---|
| 13 | `intent_phrases` | live (generated suggestions, marked `basis: suggested`) |
| 14 | `long_tail_keywords` | live |
| 15 | `buyer_questions` | live |
| 16 | `search_phrases` | live |
| 18 | `cluster_ids` | live |
| 44 | `keyword_graph_coverage` | live |
| 45 | `keyword_product_matches` | live (needs `client_product_id` in the request) |

### Title: merchandising

| id | name | availability |
|---:|---|---|
| 19 | `category_paths` | source pending |
| 20 | `taxonomy_mappings` | source pending |
| 21 | `collection_suggestions` | live |
| 22 | `facets` | live |
| 23 | `related_product_types` | live |
| 24 | `alternative_product_types` | live |
| 25 | `compatibility` | live (empty when the title states none) |
| 26 | `variant_dimensions` | live |
| 27 | `missing_attributes` | live |
| 28 | `localized_terms` | source pending (English only today; `market` returns `422 unsupported_market`) |

### Title: keyword metrics

Observed metrics attached to keyword records. Numbers are search metrics, not sales.

| id | name | availability |
|---:|---|---|
| 29 | `cpc` | live |
| 30 | `search_volume` | live |
| 31 | `paid_search_competition` | live |
| 32 | `demand_trend` | live |
| 33 | `monthly_demand` | live |
| 41 | `keyword_intent_stages` | live (modeled classification) |
| 42 | `keyword_bid_range` | live |
| 43 | `competition_index` | live |

### Research

| id | name | availability |
|---:|---|---|
| 34 | `geographic_demand` | source pending |
| 35 | `market_coverage` | live |
| 36 | `demand_supply_opportunities` | live |
| 60 | `segment_attribute_distribution` | live |
| 61 | `brand_presence` | live |
| 62 | `seller_concentration` | live |
| 63 | `merchant_type_assortment` | live |
| 64 | `intent_dimension_profile` | live |
| 65 | `dimension_cooccurrence` | live |
| 66 | `weekly_market_presence` | live |
| 67 | `listing_density` | live |
| 68 | `comparable_listings` | live |

### Content

| id | name | availability |
|---:|---|---|
| 37 | `ad_topics` | live (needs `sem` channel) |
| 38 | `blog_topics` | live |
| 39 | `video_topics` | live (needs a video channel) |
| 40 | `content_prompts` | live |
| 46 | `keyword_content_groups` | live (source must include keyword parameters) |
| 47 | `buyer_journey_questions` | live |
| 48 | `audience_fit` | live |
| 49 | `content_brief` | live |
| 50 | `content_drafts` | live |
| 51 | `first_test` | live |

### Not available to developer keys

Parameters 52 to 59 (`catalog_summary`, `catalog_dimension_summary`, `catalog_groups`, `group_members`, `ungrouped_items`, `keyword_competition_distribution`, `catalog_distinctive_themes`, `attribute_coverage`) belong to the batch and grouping endpoints and are blocked for developer keys.

## Response model

- The response is a flat JSON object whose keys are exactly the parameters you requested, and nothing else. Even `title` appears only if you asked for it.
- A parameter can hold a structured value. Keyword parameters return records, each with an `id`, the keyword `text`, and the requested measurement. A single keyword can carry its own measurement context (`market`, `language`, `currency`, `measurement_period`), and unknown context is `null`.
- A field with no value for this input comes back empty, `null` or `[]`, not invented. That is a successful answer.
- Generated phrasing (for example `intent_phrases`) is marked `basis: suggested` so you can tell it apart from observed data.
- Do not sum duplicate keyword records across products or clusters. A keyword that applies to several products links to each.

Example keyword records from `search_volume`:

```json
{
  "search_volume": [
    { "id": "13654206", "text": "Outdoor waterproof tents", "search_volume": 260 },
    { "id": "13654207", "text": "Tents for heavy rain", "search_volume": 20 },
    { "id": "13654203", "text": "Top waterproof tents for backpacking", "search_volume": null }
  ]
}
```

## Errors

Every error is a JSON envelope:

```json
{ "code": "invalid_request", "message": "The request is invalid.", "request_id": "...", "retryable": false, "details": {} }
```

Branch on `code`, not on the HTTP status alone. Keep the `request_id` for support.

| Status | `code` | Meaning and what to do |
|---|---|---|
| 401 | `invalid_key` | Missing or bad key. Check the `Authorization` header. |
| 402 | insufficient credits | Wallet is empty. Wait for the daily refill or add funds. |
| 403 | `insufficient_scope` | The route is not available to your key (batch and grouping). Do not retry. |
| 409 | `idempotency_conflict` | Same `Idempotency-Key` with a different body. Use a new key for a new request. |
| 410 | `expired` | The saved idempotent operation aged out. Send a fresh request with a new key. |
| 422 | `invalid_request` and related | Validation failed: unknown parameter, wrong endpoint for a parameter, empty selection, a parameter missing its prerequisite (`unsupported_subject_selection`, `unsupported_content_source`, `keywords_required`, `unsupported_market`). Fix the request. |
| 429 | rate limited | Daily title limit reached. See `api_limit_resets_at` from `/v1/usage`. |
| 503 | `source_unavailable` | The parameter has no verified source yet. Not billed. |
| 503 | `billing_unavailable` | The billing backend is momentarily unreachable. Retry with the same `Idempotency-Key`. |

## Idempotency and saved results

- Send an `Idempotency-Key` on every `POST`. Repeating the same key with the same body returns the saved answer with no new work and no new charge, for as long as the saved operation lives.
- The same key with a different body is a conflict (`409`).
- A saved operation expires after about a day. After that a repeat is new work (`410` on the stale key; send a fresh request).
- `GET /v1/{resource}/{id}` reads a saved result with no model call and no charge. Use the `Location` header from a `POST` to find the saved id.

## Performance

- Light parameters (`product_type`, `attributes`, `seasons`, and the research aggregates) return in roughly 2 seconds or less.
- Keyword and retrieval parameters are heavier. `long_tail_keywords`, `search_phrases`, `search_volume`, `cpc`, `keyword_intent_stages` and especially `buyer_questions` can take 8 to 25 seconds, because they retrieve and score many keyword records.
- Set a generous client timeout. The server deadline is 120 seconds. Request only the parameters you need, and prefer a saved `GET` over repeating a `POST`.

## Versioning

`GET /v1/versions` reports three independent versions: `dataset_version` (the catalog snapshot), `schema_version` (the response contract), and `matcher_version` (the matching model). The response contract is additive within a major version. Read fields you know and ignore the rest.
