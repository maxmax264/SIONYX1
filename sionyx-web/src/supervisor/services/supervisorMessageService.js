import { ref, get, push, set, update } from 'firebase/database';
import { database } from '../../config/firebase';

export const getSupervisorDisplayName = async (supervisorId) => {
  try {
    const snap = await get(ref(database, `supervisors/${supervisorId}/displayName`));
    return { success: true, displayName: snap.exists() ? snap.val() : '' };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const updateSupervisorDisplayName = async (supervisorId, displayName) => {
  try {
    await update(ref(database, `supervisors/${supervisorId}`), { displayName: displayName.trim() });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getOrgMessages = async orgId => {
  try {
    const snap = await get(ref(database, `organizations/${orgId}/messages`));
    if (!snap.exists()) return { success: true, messages: [] };

    const data = snap.val();
    const messages = Object.entries(data)
      .filter(([, msg]) => msg.fromSupervisor === true)
      .map(([id, msg]) => ({ id, ...msg }));
    messages.sort((a, b) => b.timestamp - a.timestamp);
    return { success: true, messages };
  } catch (error) {
    return { success: false, error: error.message, messages: [] };
  }
};

export const getOrgUserReplies = async (orgId) => {
  try {
    const snap = await get(ref(database, `organizations/${orgId}/userReplies`));
    if (!snap.exists()) return { success: true, replies: [] };
    const replies = Object.entries(snap.val())
      .filter(([, r]) => r.fromSupervisorReply === true)
      .map(([id, r]) => ({ id, ...r, isReply: true }));
    return { success: true, replies };
  } catch (error) {
    return { success: false, error: error.message, replies: [] };
  }
};

export const sendSupervisorMessage = async (orgId, toUserId, messageText, supervisorId) => {
  try {
    const messagesRef = ref(database, `organizations/${orgId}/messages`);
    const newRef = push(messagesRef);

    await set(newRef, {
      fromAdminId: supervisorId,
      fromSupervisor: true,
      toUserId,
      message: messageText.trim(),
      timestamp: Date.now(),
      read: false,
    });

    return { success: true, messageId: newRef.key };
  } catch (error) {
    return { success: false, error: error.message };
  }
};
