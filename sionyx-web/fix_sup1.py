content = open(r'.\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()
old = """export const sendSupervisorMessage = async (orgId, toUserId, messageText, supervisorId) => {"""
new = """export const getOrgUserReplies = async (orgId) => {
  try {
    const snap = await get(ref(database, `organizations/${orgId}/userReplies`));
    if (!snap.exists()) return { success: true, replies: [] };
    const replies = Object.entries(snap.val()).map(([id, r]) => ({
      id, ...r, isReply: true, fromSupervisorReply: r.fromSupervisorReply || false,
    }));
    return { success: true, replies };
  } catch (error) {
    return { success: false, error: error.message, replies: [] };
  }
};

export const sendSupervisorMessage = async (orgId, toUserId, messageText, supervisorId) => {"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
