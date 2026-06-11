content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\realtimeService.js', encoding='utf-8').read()

new_func = '''
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
'''

content += new_func
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\realtimeService.js', 'w', encoding='utf-8').write(content)
print('Done')
