content = open(r'.\src\services\chatService.js', encoding='utf-8').read()
old = """/**
 * Update user's last seen timestamp
 */"""
new = """/**
 * Delete a message by ID
 */
export const deleteMessage = async (orgId, messageId) => {
  try {
    await remove(ref(database, `organizations/${orgId}/messages/${messageId}`));
    return { success: true };
  } catch (error) {
    logger.error('Error deleting message:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Update user's last seen timestamp
 */"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\chatService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
