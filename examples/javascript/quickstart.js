// Reach Dog Title & Cluster API: JavaScript quickstart (Node 18+).
//
// Sends a product title and asks for three parameters, then prints the response.
// Reads the key from the TITLE_API_KEY environment variable. Never hardcode your key.
//
//   export TITLE_API_KEY=your_key_here   # (Windows: set TITLE_API_KEY=...)
//   node quickstart.js

import { randomUUID } from "node:crypto";

const BASE_URL = (
  process.env.TITLE_API_URL || "https://title-cluster-api-221381283627.us-east1.run.app"
).replace(/\/$/, "");

const KEY = (process.env.TITLE_API_KEY || "").trim();
if (!KEY) {
  console.error("Set TITLE_API_KEY in your environment.");
  process.exit(1);
}

async function ask(title, parameters) {
  const resp = await fetch(`${BASE_URL}/v1/title-matches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      "Idempotency-Key": randomUUID(),
    },
    body: JSON.stringify({ title, parameters }),
  });
  const body = await resp.json();
  if (!resp.ok) {
    // Error envelopes carry code / message / request_id / retryable.
    throw new Error(
      `${resp.status} ${body.code}: ${body.message} (request_id=${body.request_id})`
    );
  }
  return body;
}

const result = await ask("4 person camping tent waterproof", [
  "product_type",
  "attributes",
  "synonyms",
]);
console.log(JSON.stringify(result, null, 2));
