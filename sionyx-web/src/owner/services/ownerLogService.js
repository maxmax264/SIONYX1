import { ownerAuth } from "../../config/firebase";
import { getUnderstoodBase } from "../../services/serverResolver";

// getUnderstoodBase() returns the local PC's address when failover has
// switched to it, or null (falling back to this same Render URL, unchanged)
// otherwise - see services/serverResolver.js.
const getBridgeBaseUrl = () =>
  getUnderstoodBase() ||
  (import.meta.env.VITE_PAYMENT_BRIDGE_URL || "https://understood-main.onrender.com").replace(/\/$/, "");

const authedFetch = async (path, options = {}) => {
  const currentUser = ownerAuth.currentUser;
  if (!currentUser) return { success: false, error: "לא מחובר" };
  const idToken = await currentUser.getIdToken();
  const response = await fetch(`${getBridgeBaseUrl()}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    return { success: false, error: (payload && payload.error) || "שגיאה בתקשורת עם השרת" };
  }
  return payload || { success: true };
};

/** List every computer that has ever shipped a log/status ({id, name}). */
export const getLogComputers = () => authedFetch("/logs/computers");

/** Raw log tail (capped, newest-first) + structured install-status checklist for one computer. */
export const getComputerLogs = (computerId) => authedFetch(`/logs/${encodeURIComponent(computerId)}`);

/** Deletes one computer's logs+status. */
export const deleteComputerLogs = (computerId) =>
  authedFetch(`/logs/${encodeURIComponent(computerId)}`, { method: "DELETE" });

/** Deletes every computer's logs+status (bulk wipe). */
export const deleteAllLogs = () => authedFetch("/logs", { method: "DELETE" });

/**
 * Log-shipping control (applied live by every kiosk):
 * { autoEnabled, mode: "internal"|"external", intervalMs, external: { url, apiKey, format } }
 * autoEnabled is false by default - nothing is sent unless "send now" is pressed.
 */
export const getLogConfig = () => authedFetch("/logs/config");

export const saveLogConfig = (config) =>
  authedFetch("/logs/config", { method: "PUT", body: JSON.stringify({ config }) });

/** "Send logs now": one kiosk when computerId is given, otherwise every kiosk. */
export const requestLogSend = (computerId) =>
  authedFetch("/logs/trigger", {
    method: "POST",
    body: JSON.stringify(computerId ? { computerId } : {}),
  });
