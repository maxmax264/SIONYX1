// Client side of the SIONYX billing system (what an organization owes the
// platform owner). All money logic lives on the bridge (render-service/billing.js);
// this file only talks to it and listens to the org's billing status in Firebase.
import { ref, onValue } from 'firebase/database';
import { database, auth } from '../config/firebase';
import { getUnderstoodBase } from './serverResolver';

const getBridgeBaseUrl = () =>
  getUnderstoodBase() ||
  (import.meta.env.VITE_PAYMENT_BRIDGE_URL || 'https://understood-main.onrender.com').replace(/\/$/, '');

const post = async (path, body) => {
  const user = auth.currentUser;
  if (!user) throw new Error('לא מחובר');
  const token = await user.getIdToken();
  const res = await fetch(`${getBridgeBaseUrl()}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || json.success === false) {
    const err = new Error(json.error || `שגיאה (${res.status})`);
    err.code = json.code;
    throw err;
  }
  return json;
};

export const getBillingSummary = orgId => post('/billing/summary', { orgId });
export const getPayConfig = (orgId, month) => post('/billing/payConfig', { orgId, month });
export const confirmBillingPayment = (orgId, month, transactionId) =>
  post('/billing/confirm', { orgId, month, transactionId });
export const acceptContract = (orgId, data) => post('/billing/acceptContract', { orgId, ...data });

/**
 * Live view of an org's billing state. Calls back with
 * { state: 'free'|'ok'|'warning'|'blocked'|null, reason, blockAt, daysLeft,
 *   amountDue, message, loaded } and re-fires instantly when the owner blocks /
 * unblocks the org, or when a payment is recorded.
 */
export const subscribeBillingState = (orgId, callback) => {
  let status = null;
  let settings = null;
  let gotStatus = false;
  let gotSettings = false;
  const emit = () => {
    if (!gotStatus || !gotSettings) return;
    const s = settings || {};
    const st = status || {};
    let state = st.state || null;
    let reason = st.reason || null;
    let message = st.message || '';
    if (s.exempt === true) state = 'free';
    else if (s.manualBlock === true) {
      state = 'blocked';
      reason = 'manual';
      message = s.blockMessage || '';
    } else if (state === 'blocked' && st.reason === 'manual') {
      // manual flag was cleared but the stored status hasn't caught up yet
      state = 'ok';
      reason = null;
    }
    callback({
      state, reason, message, loaded: true,
      blockAt: st.blockAt || null, daysLeft: st.daysLeft || null, amountDue: st.amountDue || 0,
      invoiceMonth: st.invoiceMonth || null,
    });
  };
  const noop = () => {};
  const u1 = onValue(ref(database, `billing/orgs/${orgId}/status`), snap => {
    status = snap.val(); gotStatus = true; emit();
  }, noop);
  const u2 = onValue(ref(database, `billing/orgs/${orgId}/settings`), snap => {
    settings = snap.val(); gotSettings = true; emit();
  }, noop);
  return () => { u1(); u2(); };
};
