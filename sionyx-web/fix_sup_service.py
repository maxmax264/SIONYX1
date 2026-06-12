content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()

old = "import { ref, get, push, set, update } from 'firebase/database';"
new = "import { ref, get, push, set, update, remove } from 'firebase/database';"

content = content.replace(old, new, 1)

# Add delete functions at end
content += """
export const deleteSupervisorMessage = async (orgId, messageId) => {
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
};
"""

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
print('Done')
