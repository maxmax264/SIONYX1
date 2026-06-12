content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', encoding='utf-8').read()

old = "export const deleteMessage = async (orgId, messageId) => {"

new = """export const deleteUserReply = async (orgId, replyId) => {
  try {
    await remove(ref(database, `organizations/${orgId}/userReplies/${replyId}`));
    return { success: true };
  } catch (error) {
    logger.error('Error deleting reply:', error);
    return { success: false, error: error.message };
  }
};

export const deleteMessage = async (orgId, messageId) => {"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
