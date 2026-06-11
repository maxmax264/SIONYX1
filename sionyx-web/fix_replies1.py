content = open(r'.\src\services\chatService.js', encoding='utf-8').read()
old = """/**
 * Delete a message by ID
 */"""
new = """/**
 * Get user replies for a specific user
 */
export const getUserReplies = async (orgId, userId) => {
  try {
    const repliesRef = ref(database, `organizations/${orgId}/userReplies`);
    const snapshot = await get(repliesRef);
    if (!snapshot.exists()) return { success: true, replies: [] };
    const replies = [];
    snapshot.forEach(child => {
      const data = child.val();
      if (data.fromUserId === userId) {
        replies.push({ id: child.key, ...data, isReply: true });
      }
    });
    return { success: true, replies };
  } catch (error) {
    logger.error('Error getting user replies:', error);
    return { success: false, error: error.message, replies: [] };
  }
};

/**
 * Delete a message by ID
 */"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\chatService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
