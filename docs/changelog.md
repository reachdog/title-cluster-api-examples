# Changelog

How the API is versioned, and what the current public contract provides. New entries go at the top as the contract changes.

## Versioning

`GET /v1/versions` reports three independent version strings:

- `schema_version` is the response contract. Within a major version it is additive: new fields are added without removing the ones already there, so read the fields you know and ignore the rest.
- `dataset_version` is the catalog snapshot the answers are drawn from.
- `matcher_version` is the matching model.

The OpenAPI document at `/openapi.json` carries the API version and the request and response schemas. Not every change is a schema change: pricing and model-quality updates can ship without a new `schema_version`.

## Current contract

As of 2026-10-09:

- OpenAPI `0.2.0`
- `schema_version` `2026-09-30.4`
- `dataset_version` `registry-2026-07-21`
- `matcher_version` `catalog-matching-v0.2.0`

What this contract provides:

- Per-parameter selection. You request named parameters and the response holds exactly those, as flat top-level fields.
- Endpoints: `title-matches`, `market-research`, `content-generations`, `usage`, `versions`. Batch and catalog-grouping are not available to developer keys.
- Pricing: 25 tokens per parameter at current pricing, billed on success only, with a free daily allowance. Check `/v1/usage` for your current price, balance and limits.

This changelog starts from the current published contract. Earlier iterations predate it and are not itemized here.

## Entry format

Each future change gets an entry like this, newest first:

```
## 2026-MM-DD

Schema: <schema_version if it changed, else "no change">

Added:
- <new parameter, field or endpoint>

Changed:
- <behavior or shape change, with the before and after>

Fixed:
- <corrected behavior>

Deprecated:
- <what is going away, and the replacement>
```

Keep entries specific: name the parameter or field, and state the before and after so a developer can tell whether their integration is affected.
