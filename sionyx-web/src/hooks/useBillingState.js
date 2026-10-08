import { useEffect, useState } from 'react';
import { subscribeBillingState, getBillingSummary } from '../services/billingService';

const DAY = 24 * 60 * 60 * 1000;

/**
 * Live billing state of the current org (see billingService.subscribeBillingState),
 * plus two housekeeping jobs: it asks the bridge to (re)compute the org's status
 * on mount and every 15 minutes (that is what issues new monthly invoices), and
 * it flips "warning" to "blocked" on the client the moment the deadline passes.
 * Free (exempt) orgs always come back as state 'free'.
 */
export const useBillingState = orgId => {
  const [raw, setRaw] = useState({ state: null, loaded: false });
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    if (!orgId) return undefined;
    const unsub = subscribeBillingState(orgId, setRaw);
    const refresh = () => getBillingSummary(orgId).catch(() => {});
    refresh();
    const t1 = setInterval(refresh, 15 * 60 * 1000);
    const t2 = setInterval(() => setNow(Date.now()), 30 * 1000);
    return () => { unsub(); clearInterval(t1); clearInterval(t2); };
  }, [orgId]);

  if (raw.state === 'warning' && raw.blockAt && now > raw.blockAt) {
    return { ...raw, state: 'blocked', reason: 'unpaid' };
  }
  if (raw.state === 'warning' && raw.blockAt) {
    return { ...raw, daysLeft: Math.max(1, Math.ceil((raw.blockAt - now) / DAY)) };
  }
  return raw;
};
