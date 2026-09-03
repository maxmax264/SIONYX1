import { ref, get, update, push, set } from "firebase/database";
import { ownerDatabase as database, ownerAuth } from "../../config/firebase";

const BRIDGE_BASE_URL = (
  import.meta.env.VITE_PAYMENT_BRIDGE_URL || "https://understood-n5ok.onrender.com"
).replace(/\/$/, "");

/**
 * Flattens users across every organization into a single list, each
 * tagged with its orgId/orgName, for the owner's cross-org users view.
 * Relies on the same broad `organizations` read access the org-summary
 * dashboard (getAllOrgs) already uses - no separate permission needed.
 */
export const getAllUsersAcrossOrgs = async () => {
  try {
    const snap = await get(ref(database, "organizations"));
    if (!snap.exists()) return { success: true, users: [] };
    const data = snap.val();
    const users = [];
    Object.keys(data).forEach((orgId) => {
      const org = data[orgId];
      const orgName = org.metadata?.name || orgId;
      const orgUsers = org.users || {};
      Object.keys(orgUsers).forEach((uid) => {
        users.push({
          uid,
          orgId,
          orgName,
          ...orgUsers[uid],
        });
      });
    });
    users.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    return { success: true, users };
  } catch (e) {
    return { success: false, error: e.message, users: [] };
  }
};

/**
 * Same logic as userService.adjustUserBalance, but callable by the owner
 * for ANY org - requires the owner-bypass added to remainingTime/
 * printBalance write rules in database.rules.json (root.child('owners')
 * .child(auth.uid).exists()).
 */
export const ownerAdjustUserBalance = async (orgId, userId, adjustments) => {
  try {
    const userRef = ref(database, `organizations/${orgId}/users/${userId}`);
    const snapshot = await get(userRef);
    if (!snapshot.exists()) return { success: false, error: "User not found" };

    const currentUser = snapshot.val();
    const updates = { updatedAt: new Date().toISOString() };

    if (adjustments.timeSeconds !== undefined) {
      updates.remainingTime = Math.max(0, (currentUser.remainingTime || 0) + adjustments.timeSeconds);
    }
    if (adjustments.prints !== undefined) {
      updates.printBalance = Math.max(0, (currentUser.printBalance || 0) + adjustments.prints);
    }

    await update(userRef, updates);

    const timeDiff = adjustments.timeSeconds || 0;
    const printsDiff = adjustments.prints || 0;
    if (timeDiff !== 0 || printsDiff !== 0) {
      const purchasesRef = ref(database, `organizations/${orgId}/purchases`);
      const newRef = push(purchasesRef);
      await set(newRef, {
        userId,
        type: "owner_charge",
        status: "completed",
        createdAt: new Date().toISOString(),
        timeSeconds: timeDiff,
        prints: printsDiff,
      });
    }

    return {
      success: true,
      newBalance: {
        remainingTime: updates.remainingTime ?? currentUser.remainingTime ?? 0,
        printBalance: updates.printBalance ?? currentUser.printBalance ?? 0,
      },
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
};

export const getOrgUserPassword = async (orgId, userId) => {
  try {
    const currentUser = ownerAuth.currentUser;
    if (!currentUser) return { success: false, error: "לא מחובר" };
    const idToken = await currentUser.getIdToken();

    const response = await fetch(`${BRIDGE_BASE_URL}/getOrgUserPassword`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${idToken}` },
      body: JSON.stringify({ data: { orgId, userId } }),
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      const msg = (payload && payload.error && payload.error.message) || "שגיאה בקבלת הסיסמה";
      return { success: false, error: msg };
    }
    const result = (payload && payload.result) || {};
    return {
      success: true,
      available: !!result.available,
      password: result.password || "",
      message: result.message || "",
    };
  } catch (e) {
    return { success: false, error: e.message || "שגיאה בקבלת הסיסמה" };
  }
};