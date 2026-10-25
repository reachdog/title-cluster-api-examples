import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';

function run({ envFile, key = '', response = 'ok', expectedKey = 'test-file-key' } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'reachdog-quickstart-'));
  try {
    const folder = join(root, 'examples', 'javascript');
    mkdirSync(folder, { recursive: true });
    copyFileSync(new URL('../quickstart.js', import.meta.url), join(folder, 'quickstart.js'));
    writeFileSync(join(folder, 'package.json'), '{"type":"module"}');
    if (envFile !== undefined) writeFileSync(join(root, '.env'), envFile);
    const preload = join(root, 'mock-fetch.cjs');
    writeFileSync(preload, `
      global.fetch = async (url, init) => {
        require('node:assert/strict').equal(init.headers.Authorization, 'Bearer ' + process.env.EXPECTED_KEY);
        if (process.env.TEST_RESPONSE === 'html') return new Response('<html>Gateway error</html>', {status: 502});
        if (process.env.TEST_RESPONSE === 'json-error') return new Response(JSON.stringify({code:'invalid_request',message:'Bad selection',request_id:'test-request'}), {status:422});
        return new Response(JSON.stringify({product_type:'tent'}), {status:200});
      };
    `);
    return spawnSync(process.execPath, ['--require', preload, join(folder, 'quickstart.js')], {
      cwd: tmpdir(), encoding: 'utf8', timeout: 10000,
      env: { ...process.env, NODE_OPTIONS: '', TITLE_API_KEY: key, EXPECTED_KEY: expectedKey, TEST_RESPONSE: response },
    });
  } finally {
    assert.equal(dirname(resolve(root)), resolve(tmpdir()));
    rmSync(root, { recursive: true }); // Only this test's mkdtemp directory.
  }
}

test('loads the repository .env independently of the working directory', () => {
  const result = run({ envFile: '# Local key\r\nTITLE_API_KEY=test-file-key\r\n' });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), { product_type: 'tent' });
  assert.doesNotMatch(result.stdout + result.stderr, /test-file-key/);
});

test('an explicit environment key takes precedence', () => {
  const result = run({ envFile: 'TITLE_API_KEY=test-file-key', key: 'test-env-key', expectedKey: 'test-env-key' });
  assert.equal(result.status, 0, result.stderr);
});

test('a missing key fails before making a request', () => {
  const result = run();
  assert.equal(result.status, 1);
  assert.match(result.stderr, /environment or in a .env file at the repo root/);
  assert.doesNotMatch(result.stderr, /AssertionError/);
});

test('an HTML gateway error reports HTTP status without raw HTML or a parsing error', () => {
  const result = run({ key: 'test-file-key', response: 'html' });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /HTTP 502: API returned a non-JSON response/);
  assert.doesNotMatch(result.stderr, /SyntaxError|<html>|test-file-key/);
});

test('structured API errors retain their code and request ID', () => {
  const result = run({ key: 'test-file-key', response: 'json-error' });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /422 invalid_request: Bad selection \(request_id=test-request\)/);
});
