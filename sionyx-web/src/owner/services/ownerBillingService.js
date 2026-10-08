import { ownerAuth } from "../../config/firebase";
import { getUnderstoodBase } from "../../services/serverResolver";

const getBridgeBaseUrl = () =>
  getUnderstoodBase() ||
  (import.meta.env.VITE_PAYMENT_BRIDGE_URL || "https://understood-main.onrender.com").replace(/\/$/, "");

const post = async (path, body) => {
  const user = ownerAuth.currentUser;
  if (!user) throw new Error("לא מחובר");
  const token = await user.getIdToken();
  const res = await fetch(`${getBridgeBaseUrl()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(body || {}),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || json.success === false) throw new Error(json.error || `שגיאה (${res.status})`);
  return json;
};

export const getBillingOverview = () => post("/billing/overview");
export const runBillingForAll = () => post("/billing/runAll");
export const billingAction = (orgId, action, params) => post("/billing/ownerAction", { orgId, action, params });
export const saveBillingConfig = params => post("/billing/ownerAction", { action: "saveConfig", params });
export const saveBillingApiValid = apiValid => post("/billing/ownerAction", { action: "saveApiValid", params: { apiValid } });
