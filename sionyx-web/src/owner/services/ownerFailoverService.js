import { ref, get, update } from "firebase/database";
import { ownerDatabase as database, ownerAuth } from "../../config/firebase";

// Global (not per-org) failover switch, read by both the kiosk's
// ServerResolver.cs and the dashboard's serverResolver.js - see the SIONYX
// failover plan doc. Lives under systemSettings, same DB node the owner
// dashboard already uses for maxImageSizeMB, protected by the same rule
// (any signed-in user can read, only an owner can write - database.rules.json).
const PATH = "systemSettings/failover";

export const getFailoverSettings = async () => {
  try {
    const snap = await get(ref(database, PATH));
    const data = snap.exists() ? snap.val() : {};
    return { success: true, mode: data?.mode === "forceRender" || data?.mode === "forceLocal" ? data.mode : "auto" };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const updateFailoverMode = async (mode) => {
  if (mode !== "auto" && mode !== "forceRender" && mode !== "forceLocal") {
    return { success: false, error: "מצב לא תקין" };
  }
  try {
    await update(ref(database, PATH), {
      mode,
      updatedAt: Date.now(),
      updatedBy: ownerAuth.currentUser?.email || ownerAuth.currentUser?.uid || "unknown",
    });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};
