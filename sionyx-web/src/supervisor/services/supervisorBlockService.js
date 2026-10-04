import { ref, get, set, remove, update } from 'firebase/database';
import { supervisorDatabase as database, supervisorAuth as auth } from '../../config/firebase';
import { useSupervisorAuthStore } from '../store/supervisorAuthStore';

export const blockUser = async (phone, reason, userName) => {
  try {
    const user = auth.currentUser;
    if (!user) return { success: false, error: 'Not authenticated' };

    const normalizedPhone = phone.replace(/\D/g, '');
    if (!normalizedPhone) return { success: false, error: 'Invalid phone number' };

    const orgIds = useSupervisorAuthStore.getState().getOrgIds();
    if (orgIds.length === 0) return { success: false, error: 'No supervised organizations' };

    const blockedRef = ref(database, `supervisors/${user.uid}/blockedUsers/${normalizedPhone}`);
    await set(blockedRef, {
      name: userName || '',
      reason: reason || '',
      blockedAt: Date.now(),
      blockedBy: user.uid,
    });

    let blockedCount = 0;
    for (const orgId of orgIds) {
      await set(ref(database, `organizations/${orgId}/blockedPhones/${normalizedPhone}`), {
        blockedAt: Date.now(),
        blockedBy: user.uid,
      });
      const usersRef = ref(database, `organizations/${orgId}/users`);
      const usersSnap = await get(usersRef);
      if (!usersSnap.exists()) continue;

      const users = usersSnap.val();
      for (const [userId, userData] of Object.entries(users)) {
        const userPhone = (userData.phoneNumber || '').replace(/\D/g, '');
        if (userPhone === normalizedPhone) {
          const userRef = ref(database, `organizations/${orgId}/users/${userId}`);
          await update(userRef, {
            blocked: true,
            blockedAt: Date.now(),
            blockedReason: reason || '',
          });
          blockedCount++;
        }
      }
    }

    return { success: true, blockedCount, message: `User blocked in ${blockedCount} organization(s)` };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const unblockUser = async phone => {
  try {
    const user = auth.currentUser;
    if (!user) return { success: false, error: 'Not authenticated' };

    const normalizedPhone = phone.replace(/\D/g, '');
    const orgIds = useSupervisorAuthStore.getState().getOrgIds();

    const blockedRef = ref(database, `supervisors/${user.uid}/blockedUsers/${normalizedPhone}`);
    await remove(blockedRef);
    for (const orgId of orgIds) {
      await remove(ref(database, `organizations/${orgId}/blockedPhones/${normalizedPhone}`));
    }

    let unblockedCount = 0;
    for (const orgId of orgIds) {
      const usersRef = ref(database, `organizations/${orgId}/users`);
      const usersSnap = await get(usersRef);
      if (!usersSnap.exists()) continue;

      const users = usersSnap.val();
      for (const [userId, userData] of Object.entries(users)) {
        const userPhone = (userData.phoneNumber || '').replace(/\D/g, '');
        if (userPhone === normalizedPhone) {
          const userRef = ref(database, `organizations/${orgId}/users/${userId}`);
          await update(userRef, {
            blocked: false,
            blockedAt: null,
            blockedReason: null,
          });
          unblockedCount++;
        }
      }
    }

    return { success: true, unblockedCount, message: `User unblocked in ${unblockedCount} organization(s)` };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getBlockedUsers = async () => {
  try {
    const user = auth.currentUser;
    if (!user) return { success: false, error: 'Not authenticated', blockedUsers: [] };

    const blockedRef = ref(database, `supervisors/${user.uid}/blockedUsers`);
    const snapshot = await get(blockedRef);

    if (!snapshot.exists()) return { success: true, blockedUsers: [] };

    const data = snapshot.val();
    const blockedUsers = Object.keys(data).map(phone => ({
      phone,
      ...data[phone],
    }));

    blockedUsers.sort((a, b) => (b.blockedAt || 0) - (a.blockedAt || 0));
    return { success: true, blockedUsers };
  } catch (error) {
    return { success: false, error: error.message, blockedUsers: [] };
  }
};

/** Normalize an Israeli phone to local digits (05XXXXXXXX). Returns '' if invalid. */
export const normalizePhone = raw => {
  let d = String(raw || '').replace(/\D/g, '');
  if (d.startsWith('00972')) d = d.slice(5);
  else if (d.startsWith('972')) d = d.slice(3);
  if (d.length === 8 || d.length === 9) d = d.startsWith('0') ? d : `0${d}`;
  return /^0\d{8,9}$/.test(d) ? d : '';
};

/** Parse CSV/TXT text: one phone per row; optional 2nd column name, 3rd reason. */
export const parseBlockList = text => {
  const seen = new Set();
  const valid = [];
  const invalid = [];
  const lines = String(text || '').replace(/^\uFEFF/, '').split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    const cols = line.split(/[,;\t]/).map(c => c.trim().replace(/^"|"$/g, ''));
    const phone = normalizePhone(cols[0]);
    if (!phone) {
      if (/\d/.test(cols[0])) invalid.push(cols[0]);
      continue; // header / non-numeric rows are skipped
    }
    if (seen.has(phone)) continue;
    seen.add(phone);
    valid.push({ phone, name: cols[1] || '', reason: cols[2] || '' });
  }
  return { valid, invalid };
};

const MAX_PATHS_PER_UPDATE = 400;

const commitUpdates = async updates => {
  const keys = Object.keys(updates);
  for (let i = 0; i < keys.length; i += MAX_PATHS_PER_UPDATE) {
    const chunk = {};
    keys.slice(i, i + MAX_PATHS_PER_UPDATE).forEach(k => (chunk[k] = updates[k]));
    await update(ref(database), chunk);
  }
};

/** Bulk-block phones: supervisor list + flag existing users + per-org blockedPhones (for future registrations). */
export const blockUsersBulk = async (entries, defaultReason) => {
  try {
    const user = auth.currentUser;
    if (!user) return { success: false, error: 'Not authenticated' };
    const orgIds = useSupervisorAuthStore.getState().getOrgIds();
    if (orgIds.length === 0) return { success: false, error: 'No supervised organizations' };

    const now = Date.now();
    const byPhone = new Map(entries.map(e => [e.phone, e]));
    const updates = {};

    for (const [phone, e] of byPhone) {
      updates[`supervisors/${user.uid}/blockedUsers/${phone}`] = {
        name: e.name || '',
        reason: e.reason || defaultReason || '',
        blockedAt: now,
        blockedBy: user.uid,
      };
      for (const orgId of orgIds) {
        updates[`organizations/${orgId}/blockedPhones/${phone}`] = { blockedAt: now, blockedBy: user.uid };
      }
    }

    let flaggedUsers = 0;
    for (const orgId of orgIds) {
      const snap = await get(ref(database, `organizations/${orgId}/users`));
      if (!snap.exists()) continue;
      for (const [userId, u] of Object.entries(snap.val())) {
        const e = byPhone.get(normalizePhone(u.phoneNumber));
        if (!e) continue;
        const base = `organizations/${orgId}/users/${userId}`;
        updates[`${base}/blocked`] = true;
        updates[`${base}/blockedAt`] = now;
        updates[`${base}/blockedReason`] = e.reason || defaultReason || '';
        flaggedUsers++;
      }
    }

    await commitUpdates(updates);
    return { success: true, total: byPhone.size, flaggedUsers };
  } catch (error) {
    return { success: false, error: error.message };
  }
};
