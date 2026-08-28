import { ref, get, set, remove } from "firebase/database";
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
      rustdesk: c.remoteControl?.rustdesk || null,
      anydesk: c.remoteControl?.anydesk || null,
    }));
    return { success: true, computers };
  } catch (e) {
    return { success: false, error: e.message, computers: [] };
  }
};

/** Owner-only: push a new AnyDesk password for a specific kiosk. Written to the
 * `setPassword` command channel (separate from `password`, which the kiosk itself
 * uses to self-report its currently-installed password - keeping them separate
 * means the kiosk's own report is never blocked by the owner-only permission on
 * commanding a change). The kiosk's RemoteControlReportingService picks this up
 * in real time (SseListener) and applies it via `AnyDesk.exe --set-password` -
 * no reboot needed. */
export const setAnyDeskPassword = async (orgId, computerId, password) => {
  try {
    await waitForAuth();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/remoteControl/anydesk/setPassword`), password);
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
};

/** Owner-only: ask a kiosk to re-report its current RustDesk/AnyDesk ID+password.
 * Covers a failed initial report or IDs that changed (e.g. reinstall). The kiosk's
 * RemoteControlReportingService listens for this in real time and re-reports within
 * seconds - no need to touch the machine. */
export const requestRemoteControlRefresh = async (orgId, computerId) => {
  try {
    await waitForAuth();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/remoteControl/refreshRequested`), Date.now());
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
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
