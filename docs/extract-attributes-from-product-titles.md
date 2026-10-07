# Extract structured attributes from product titles

Product titles are written for humans, not for databases. "4 person camping tent waterproof" tells a shopper everything and tells your catalog almost nothing. If you want to filter by capacity, group by product type, or spot that a listing never states its material, you first have to turn that sentence into fields.

This walkthrough shows how to do that with the Reach Dog Title and Cluster API: send a title, get back a product type, a list of attributes, and the facts the title is missing. Every request and response below is real output from the API.

## The problem

Say you have a few thousand titles like these:

- `4 person camping tent waterproof`
- `stainless steel insulated water bottle 32oz`
- `womens running shoes size 8 breathable`

You want, for each one: what is it, what are its attributes, and what is it not telling you. Writing a parser by hand means a brittle pile of regexes that breaks on the next vendor's naming. This is the job the API is built for.

## Step 1: get a key

Create a developer key at https://intersect.reach.dog/developer and set it in your environment:

```bash
export TITLE_API_KEY=your_key_here
```

## Step 2: ask for what you want

You send the title and the exact parameters you want back. For attribute extraction, ask for `product_type` and `attributes`:

```bash
curl -s https://title-cluster-api-221381283627.us-east1.run.app/v1/title-matches \
  -H "Authorization: Bearer $TITLE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"title":"4 person camping tent waterproof","parameters":["product_type","attributes"]}'
```

You are billed one unit per parameter, and only when the call succeeds, so this request costs two units.

## Step 3: read the response

The response has exactly the fields you asked for and nothing else:

```json
{
  "product_type": "camping tent",
  "attributes": [
    { "name": "Capacity", "value": "4 person" },
    { "name": "Waterproof", "value": "waterproof" }
  ]
}
```

The product type is normalized to a clean label, and each attribute is a name and value pulled from the title. These facts stay grounded in the title itself. The API does not invent a material or a weight that the title never stated.

## Step 4: find what the title is missing

The useful next move for catalog quality is to ask what a good listing of this type should have but this title does not. Add `missing_attributes`:

```json
{
  "missing_attributes": ["tent material", "tent dimensions", "setup method", "number of doors", "number of rooms"]
}
```

Now you have a to-do list for each product page: the attributes worth asking the merchant to fill in.

## Handling uncertain and incomplete results

Real catalogs are messy, and the API is honest about it. Two cases to handle:

A field with no value for this title comes back empty, not fabricated. A title with no stated brand returns `null`, and a product that states no compatibility returns an empty list:

```json
{ "brand": null }
{ "compatibility": [] }
```

An empty result is still a successful answer. It means the API looked and there was nothing in the title to return, which is exactly what you want to know for a catalog-quality pass.

Some parameters depend on data that is not available yet and return a clear error rather than a guess, for example localized terms:

```json
{ "code": "unsupported_market", "message": "Title taxonomy sources do not support a market filter.", "retryable": false }
```

Branch on the error `code`, not on the HTTP status alone.

## Reproduce this

The runnable version of this walkthrough is in the examples repository:

```bash
git clone <this repo>
cd reachdog-title-api-examples/examples/python
pip install -r requirements.txt
cp ../../.env.example ../../.env   # then put your key in it
python quickstart.py
python handling_boundaries.py
```

- Code: this repository
- Live demo: the Hugging Face Space (link to be added)
- Access and pricing: https://intersect.reach.dog/developer

## Where to go next

Attributes are one parameter group. The same request shape gives you buyer keywords with real search volume, suggested collections and facets for merchandising, and market research on a whole product type. Request the parameters you need in the same call, and you only pay for the ones you ask for.
