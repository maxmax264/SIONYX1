content = open(r'.\src\services\userService.js', encoding='utf-8').read()

idx = content.find('export const deleteUser = async (orgId, userId) =>')
end = content.find('};', idx) + 2
old = content[idx:end]
print(f"Found block length: {len(old)}")
print(repr(old[:100]))

new = '''export const deleteUser = async (orgId, userId) => {
  try {
    const db = getDatabase();
    const userRef = ref(db, `organizations/${orgId}/users/${userId}`);
    const userSnap = await get(userRef);
    if (!userSnap.exists()) {
      return { success: false, error: 'המשתמש לא נמצא' };
    }
    const userData = userSnap.val();
    const messagesRef = ref(db, `organizations/${orgId}/messages`);
    const messagesSnap = await get(messagesRef);
    if (messagesSnap.exists()) {
      const updates = {};
      Object.entries(messagesSnap.val()).forEach(([msgId, msg]) => {
        if (msg.toUserId === userId) {
          updates[`organizations/${orgId}/messages/${msgId}`] = null;
        }
      });
      if (Object.keys(updates).length > 0) {
        await update(ref(db), updates);
      }
    }
    if (userData.currentComputerId) {
      const compRef = ref(db, `organizations/${orgId}/computers/${userData.currentComputerId}`);
      const compSnap = await get(compRef);
      if (compSnap.exists() && compSnap.val().currentUserId === userId) {
        await update(compRef, { currentUserId: null, isActive: false });
      }
    }
    await remove(userRef);
    return { success: true, message: 'המשתמש נמחק בהצלחה' };
  } catch (error) {
    logger.error('Error deleting user:', error);
    return { success: false, error: error.message || 'שגיאה במחיקת המשתמש' };
  }
};'''

content = content[:idx] + new + content[end:]
open(r'.\src\services\userService.js', 'w', encoding='utf-8').write(content)
print('OK')
