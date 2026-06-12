content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()

old = """export const deleteSupervisorMessage = async (orgId, messageId) => {
  try {
    await remove(ref(database, `organizations/${orgId}/messages/${messageId}`));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const deleteSupervisorReply = async (orgId, replyId) => {
  try {
    await remove(ref(database, `organizations/${orgId}/userReplies/${replyId}`));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};"""

new = """export const deleteSupervisorMessage = async (orgId, messageId) => {
  try {
    await update(ref(database, `organizations/${orgId}/messages/${messageId}`), { deleted: true });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const deleteSupervisorReply = async (orgId, replyId) => {
  try {
    await update(ref(database, `organizations/${orgId}/userReplies/${replyId}`), { deleted: true });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
