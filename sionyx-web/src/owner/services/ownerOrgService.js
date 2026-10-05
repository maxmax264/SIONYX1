import { ref, get, set, remove, onValue } from "firebase/database";
import { ownerAuth as auth, ownerDatabase as database } from "../../config/firebase";

const waitForAuth = () =>
  new Promise((resolve) => {
    if (auth.currentUser) return resolve(auth.currentUser);
    const unsub = auth.onAuthStateChanged((user) => { unsub(); resolve(user); });
  });

export const getAllOrgs = async () => {
  try {
    await waitForAuth();
    const snap = await get(ref(database, "organizations"));
    if (!snap.exists()) return { success: true, orgs: [] };
    const data = snap.val();
    const orgs = await Promise.all(Object.keys(data).map(async (orgId) => {
      const org = data[orgId];
      const users = org.users ? Object.values(org.users) : [];
      const computers = org.computers ? Object.values(org.computers) : [];
      const activeUsers = users.filter((u) => u.isSessionActive).length;
      const supervisorsSnap = await get(ref(database, "supervisors"));
      let supervisedBy = null;
      if (supervisorsSnap.exists()) {
        Object.entries(supervisorsSnap.val()).forEach(([uid, sup]) => {
          if (sup.organizations && sup.organizations[orgId]) supervisedBy = uid;
        });
      }
      return {
        orgId,
        name: org.metadata?.name || orgId,
        status: org.metadata?.status || "active",
        userCount: users.length,
        activeUsers,
        computerCount: computers.length,
        isSupervised: !!supervisedBy,
        supervisedBy,
        createdAt: org.metadata?.createdAt || null,
      };
    }));
    return { success: true, orgs };
  } catch (e) {
    return { success: false, error: e.message, orgs: [] };
  }
};

export const connectToSupervision = async (orgId, supervisorUid) => {
  try {
    await set(ref(database, `supervisors/${supervisorUid}/organizations/${orgId}`), true);
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
};

export const disconnectFromSupervision = async (orgId, supervisorUid) => {
  try {
    await remove(ref(database, `supervisors/${supervisorUid}/organizations/${orgId}`));
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
};

export const getOrgComputers = async (orgId) => {
  try {
    await waitForAuth();
    const snap = await get(ref(database, `organizations/${orgId}/computers`));
    if (!snap.exists()) return { success: true, computers: [] };
    const data = snap.val();
    const computers = Object.entries(data).map(([computerId, c]) => ({
      computerId,
      computerName: c.computerName || computerId,
      isActive: !!c.isActive,
      lastSeen: c.lastSeen || null,
    }));
    return { success: true, computers };
  } catch (e) {
    return { success: false, error: e.message, computers: [] };
  }
};

/**
 * 08/09: גרסה חיה (onValue) של getOrgComputers - נועדה לדראוור פרטי-ארגון
 * בדשבורד ה-owner, כדי שפרטי שליטה מרחוק (במיוחד ID/PIN של AeroAdmin, שמתחלף
 * לעיתים תכופות) יתעדכנו על המסך מיד, בלי לדרוש רענון ידני של הדף - בדיוק
 * כמו subscribeToComputers ב-realtimeService.js הרגיל (שכבר חי), רק בשכבת
 * ה-owner (מסד נתונים/הרשאות נפרדים).
 * @returns {Function} unsubscribe
 */
export const subscribeToOrgComputers = (orgId, callback) => {
  if (!orgId) return () => {};
  const computersRef = ref(database, `organizations/${orgId}/computers`);
  return onValue(
    computersRef,
    snapshot => {
      if (!snapshot.exists()) { callback([]); return; }
      const data = snapshot.val();
      const computers = Object.entries(data).map(([computerId, c]) => ({
        computerId,
        computerName: c.computerName || computerId,
        isActive: !!c.isActive,
        lastSeen: c.lastSeen || null,
      }));
      callback(computers);
    },
    error => {
      console.error("subscribeToOrgComputers listener error:", error.message);
    }
  );
};

export const getAllSupervisors = async () => {
  try {
    await waitForAuth();
    const snap = await get(ref(database, "supervisors"));
    if (!snap.exists()) return { success: true, supervisors: [] };
    const data = snap.val();
    const supervisors = Object.keys(data).map((uid) => ({
      uid,
      ...data[uid],
      orgIds: data[uid].organizations ? Object.keys(data[uid].organizations) : [],
    }));
    return { success: true, supervisors };
  } catch (e) {
    return { success: false, error: e.message, supervisors: [] };
  }
};
