// Watches whether the org's local PC (running Understood / sionyx-vnc-relay /
// sionyx-auth-server, see the SIONYX failover plan doc) is reachable, and
// tells callers which base URL to use RIGHT NOW - the local PC when it's
// healthy, Render when it isn't.
//
// This module is purely ADDITIVE and fails safe: every getter returns null
// unless startServerResolver() has run AND currently has an opinion, and
// null always means "use your existing pre-failover URL, unchanged".
//
// IMPORTANT BROWSER LIMITATION (unlike the kiosk's C# version of this same
// resolver): this dashboard is served over https://, and the local PC has
// no TLS yet (plan doc, Stage C not done) - it's plain http://. Browsers
// block an https:// page from fetching http:// resources ("mixed content"),
// so until Stage C ships, the health check below will always fail here and
// getUnderstoodBase()/getVncBase() will always return null (i.e. this
// dashboard keeps using Render, same as before this file existed). This is
// safe - it just means dashboard-side failover only actually activates once
// HTTPS reaches the PC. The kiosk (a desktop app, not a browser) has no such
// restriction and fails over correctly today.
import { ref, get } from 'firebase/database';
import { database } from '../config/firebase';

const LOCAL_HOST = '83.229.22.45';
const UNDERSTOOD_PORT = 3001;
const VNC_PORT = 3002;
const AUTH_PORT = 3003;

const CHECK_INTERVAL_MS = 20_000;
const HEALTH_TIMEOUT_MS = 5_000;
const FAILURES_TO_GO_REMOTE = 3;
const SUCCESSES_TO_GO_LOCAL = 3;

let localHealthy = false; // starts assuming Render, same as today, until proven healthy
let consecutiveFailures = 0;
let consecutiveSuccesses = 0;
let ownerMode = 'auto'; // 'auto' | 'forceRender' | 'forceLocal'
let started = false;

const refreshOwnerMode = async () => {
  try {
    const snap = await get(ref(database, 'systemSettings/failover'));
    const mode = snap.exists() ? snap.val()?.mode : null;
    if (mode === 'auto' || mode === 'forceRender' || mode === 'forceLocal') {
      ownerMode = mode;
    }
    // any other value (including missing/not-yet-created): leave ownerMode as-is (defaults to 'auto')
  } catch {
    // not signed in yet, or offline - leave ownerMode as-is, try again next cycle
  }
};

const checkHealth = async () => {
  let healthy = false;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
    const response = await fetch(`http://${LOCAL_HOST}:${AUTH_PORT}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    healthy = response.ok;
  } catch {
    healthy = false; // includes the expected mixed-content block pre-Stage-C (see file header)
  }

  if (healthy) {
    consecutiveFailures = 0;
    consecutiveSuccesses += 1;
    if (!localHealthy && consecutiveSuccesses >= SUCCESSES_TO_GO_LOCAL) {
      localHealthy = true;
    }
  } else {
    consecutiveSuccesses = 0;
    consecutiveFailures += 1;
    if (localHealthy && consecutiveFailures >= FAILURES_TO_GO_REMOTE) {
      localHealthy = false;
    }
  }
};

/** Starts the background watcher. Safe to call more than once - only the first call does anything. */
export const startServerResolver = () => {
  if (started) return;
  started = true;

  const tick = async () => {
    await Promise.all([refreshOwnerMode(), checkHealth()]);
  };

  tick();
  setInterval(tick, CHECK_INTERVAL_MS);
};

const isLocalActive = () => {
  if (ownerMode === 'forceLocal') return true;
  if (ownerMode === 'forceRender') return false;
  return localHealthy;
};

/** Base URL for the Understood payment bridge, or null to keep using the existing Render config unchanged. */
export const getUnderstoodBase = () => (started && isLocalActive() ? `http://${LOCAL_HOST}:${UNDERSTOOD_PORT}` : null);

/** Base URL for sionyx-auth-server, or null to keep using the existing Render config unchanged. */
export const getAuthBase = () => (started && isLocalActive() ? `http://${LOCAL_HOST}:${AUTH_PORT}` : null);

/** wss://-or-ws:// base for the VNC relay, or null to keep using the existing Render config unchanged. */
export const getVncBase = () => (started && isLocalActive() ? `ws://${LOCAL_HOST}:${VNC_PORT}` : null);
