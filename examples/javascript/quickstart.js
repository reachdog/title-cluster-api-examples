// Reach Dog Title & Cluster API: JavaScript quickstart (Node 18+).
//
// Sends a product title and asks for three parameters, then prints the response.
// Reads the key from the TITLE_API_KEY environment variable. Never hardcode your key.
//
//   export TITLE_API_KEY=your_key_here   # (Windows: set TITLE_API_KEY=...)
//   node quickstart.js

import { randomUUID } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";

function loadKey() {
  const key = (process.env.TITLE_API_KEY || "").trim();
  if (key) return key;
  const env = new URL("../../.env", import.meta.url);
  if (existsSync(env)) {
    const line = readFileSync(env, "utf8").split(/\r?\n/).find(value => value.startsWith("TITLE_API_KEY="));
    if (line) return line.slice("TITLE_API_KEY=".length).trim();
  }
  return "";
}

const BASE_URL = (
  process.env.TITLE_API_URL || "https://title-cluster-api-221381283627.us-east1.run.app"
).replace(/\/$/, "");

const KEY = loadKey();
if (!KEY) {
  console.error("Set TITLE_API_KEY in your environment or in a .env file at the repo root.");
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
  let body;
  try {
    body = await resp.json();
  } catch (error) {
    if (!(error instanceof SyntaxError)) throw error;
    throw new Error(`HTTP ${resp.status}: API returned a non-JSON response. No automatic retry was made.`);
  }
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
