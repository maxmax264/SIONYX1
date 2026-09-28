// Contract test: every field the kiosk heartbeat writes to
// computers/{id} MUST have its own child rule (.write + .validate) in
// database.rules.json.
//
// Why this exists (2026-09-28 incident): a new heartbeat field
// (tvnServiceRunning) shipped in the kiosk without a matching rule. The
// heartbeat is ONE PATCH; Realtime Database checks each written child
// against the rules, the unknown child fell back to the computer-level
// rule (org users only - an anonymous device is not one), and the WHOLE
// PATCH was rejected with 401. For ~3 hours the dashboard showed no
// kiosk as alive, and no test noticed.
//
// Run:  node --test scripts/contracts/
// Overrides (used to prove the test really detects the bug):
//   RULES_PATH=/path/to/rules.json  HEARTBEAT_SRC=/path/to/ComputerHeartbeatService.cs

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..');
const RULES_PATH = process.env.RULES_PATH ?? path.join(repo, 'database.rules.json');
const HEARTBEAT_SRC =
  process.env.HEARTBEAT_SRC ??
  path.join(repo, 'sionyx-kiosk-wpf', 'src', 'SionyxKiosk', 'Services', 'ComputerHeartbeatService.cs');

/** Keys of the Dictionary passed to DbUpdateAsync($"computers/{_computerId}", ...). */
export function extractHeartbeatKeys(csSource) {
  const call = csSource.search(/DbUpdateAsync\(\s*\$"computers\/\{_computerId\}"\s*,/);
  if (call < 0) throw new Error('heartbeat DbUpdateAsync(computers/{_computerId}) call not found');
  const end = csSource.indexOf('});', call);
  if (end < 0) throw new Error('end of heartbeat payload not found');
  const block = csSource.slice(call, end);
  const keys = [...block.matchAll(/\["([A-Za-z0-9_]+)"\]\s*=/g)].map((m) => m[1]);
  return [...new Set(keys)];
}

const rules = JSON.parse(readFileSync(RULES_PATH, 'utf8'));
const computerRules = rules.rules.organizations.$orgId.computers.$computerId;
const keys = extractHeartbeatKeys(readFileSync(HEARTBEAT_SRC, 'utf8'));

test('extractor finds the known heartbeat fields (guards the parser itself)', () => {
  for (const k of ['heartbeatAt', 'appVersion', 'tightVncInstalled', 'inputInjectorRunning']) {
    assert.ok(keys.includes(k), `parser lost "${k}" - heartbeat payload layout changed?`);
  }
  assert.ok(keys.length >= 6, `suspiciously few heartbeat keys: ${keys.join(',')}`);
});

test('every heartbeat field has a child rule with .write and .validate', () => {
  const problems = [];
  for (const k of keys) {
    const rule = computerRules[k];
    if (!rule) {
      problems.push(`${k}: no rule under computers/$computerId (whole heartbeat PATCH would 401)`);
      continue;
    }
    if (!rule['.write']) problems.push(`${k}: rule has no ".write"`);
    if (!rule['.validate']) problems.push(`${k}: rule has no ".validate"`);
  }
  assert.deepEqual(problems, [], '\n' + problems.join('\n'));
});

test('heartbeat child .write rules do not require org membership', () => {
  // The device is an anonymous identity, never an org user.
  for (const k of keys) {
    const w = String(computerRules[k]?.['.write'] ?? '');
    assert.ok(!/organizations|users|isAdmin/.test(w), `${k}: ".write" depends on org membership: ${w}`);
  }
});
