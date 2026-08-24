import { ref, onValue } from 'firebase/database';
import { database } from '../config/firebase';
import { logger } from '../utils/logger';
import { useNotificationStore } from '../store/notificationStore';

/**
 * Subscribe to real-time updates for users
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving user list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToUsers = (orgId, callback) => {
  if (!orgId) return () => {};
  const usersRef = ref(database, `organizations/${orgId}/users`);
  return onValue(
    usersRef,
    snapshot => {
      if (snapshot.exists()) {
        const users = snapshot.val();
        const userList = Object.keys(users).map(uid => ({ uid, ...users[uid] }));
        callback(userList);
      } else {
        callback([]);
      }
    },
    error => {
      logger.error('Users listener error:', error);
    }
  );
};

/**
 * Subscribe to real-time updates for the admin's own sent messages.
 * NOTE: this does NOT fire an in-app notification, since these are
 * messages the admin sent - a "new message received" popup here would
 * fire every time the admin sends something themselves. See
 * subscribeToReplies for genuine incoming-message notifications.
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving message list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToMessages = (orgId, callback) => {
  if (!orgId) return () => {};
  const messagesRef = ref(database, `organizations/${orgId}/messages`);
  return onValue(
    messagesRef,
    snapshot => {
      if (snapshot.exists()) {
        const messages = snapshot.val();
        const messageList = Object.keys(messages).map(id => ({ id, ...messages[id] })).filter(m => !m.fromSupervisor);
        callback(messageList);
      } else {
        callback([]);
      }
    },
    error => {
      logger.error('Messages listener error:', error);
    }
  );
};

// Track previous reply counts per org for new-reply notifications
const prevReplyCountByOrg = new Map();

/**
 * Subscribe to real-time updates for user replies (genuine incoming
 * messages from users, as opposed to messages the admin sent them).
 * Fires the "new message received" in-app notification only here, since
 * this is the only path that represents something actually arriving from
 * a user rather than something the admin just did.
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving reply list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToReplies = (orgId, callback) => {
  if (!orgId) return () => {};
  const repliesRef = ref(database, `organizations/${orgId}/userReplies`);
  return onValue(
    repliesRef,
    snapshot => {
      if (snapshot.exists()) {
        const repliesData = snapshot.val();
        const replyList = Object.keys(repliesData)
          .map(id => ({ id, ...repliesData[id], isReply: true }))
          .filter(r => !r.fromSupervisorReply);
        const prevCount = prevReplyCountByOrg.get(orgId) ?? 0;
        if (prevCount > 0 && replyList.length > prevCount) {
          useNotificationStore.getState().addNotification({
            type: 'message',
            message: 'הודעה חדשה התקבלה',
          });
        }
        prevReplyCountByOrg.set(orgId, replyList.length);
        callback(replyList);
      } else {
        prevReplyCountByOrg.set(orgId, 0);
        callback([]);
      }
    },
    error => {
      logger.error('Replies listener error:', error);
    }
  );
};

/**
 * Subscribe to real-time updates for computers
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving computer list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToComputers = (orgId, callback) => {
  if (!orgId) return () => {};
  const computersRef = ref(database, `organizations/${orgId}/computers`);
  return onValue(
    computersRef,
    snapshot => {
      if (snapshot.exists()) {
        const computers = snapshot.val();
        const computerList = Object.keys(computers).map(id => ({ id, ...computers[id] }));
        callback(computerList);
      } else {
        callback([]);
      }
    },
    error => {
      logger.error('Computers listener error:', error);
    }
  );
};

/**
 * Subscribe to real-time updates for announcements
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving announcement list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToAnnouncements = (orgId, callback) => {
  if (!orgId) return () => {};
  const announcementsRef = ref(database, `organizations/${orgId}/announcements`);
  return onValue(
    announcementsRef,
    snapshot => {
      if (snapshot.exists()) {
        const announcements = snapshot.val();
        const list = Object.keys(announcements).map(id => ({ id, ...announcements[id] }));
        callback(list);
      } else {
        callback([]);
      }
    },
    error => {
      logger.error('Announcements listener error:', error);
    }
  );
};

/**
 * Subscribe to real-time updates for user replies
 * @param {string} orgId - Organization ID
 * @param {Function} callback - Callback receiving replies list
 * @returns {Function} Unsubscribe function
 */
export const subscribeToUserReplies = (orgId, callback) => {
  if (!orgId) return () => {};
  const repliesRef = ref(database, `organizations/${orgId}/userReplies`);
  return onValue(
    repliesRef,
    snapshot => {
      if (snapshot.exists()) {
        const replies = snapshot.val();
        const replyList = Object.keys(replies).map(id => ({ id, ...replies[id], isReply: true }));
        callback(replyList);
      } else {
        callback([]);
      }
    },
    error => {
      logger.error('UserReplies listener error:', error);
    }
  );
};
