content = open(r'.\src\services\userService.js', encoding='utf-8').read()

old = '''export const deleteUser = async (orgId, userId) => {
  try {
    const deleteUserFn = httpsCallable(functions, 'deleteUser');
    const result = await deleteUserFn({ orgId, userId });
    return {
      success: true,
      message: result.data.message || 'המשתמש נמחק בהצלחה',
    };
  } catch (error) {
    logger.error('Error deleting user:', error);
    const errorMessage = error.message || 'שגיאה במחיקת המשתמש';
    return { success: false, error: errorMessage };
  }
};'''

new = '''export const deleteUser = async (orgId, userId) => {
  try {
    const db = getDatabase();
    const userRef = ref(db, `organizations/${orgId}/users/${userId}`);
    const userSnap = await get(userRef);
    if (!userSnap.exists()) {
      return { success: false, error: 'המשתמש לא נמצא' };
    }
    const userData = userSnap.val();
    // Delete messages sent to this user
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
    // Clear computer association
    if (userData.currentComputerId) {
      const compRef = ref(db, `organizations/${orgId}/computers/${userData.currentComputerId}`);
      const compSnap = await get(compRef);
      if (compSnap.exists() && compSnap.val().currentUserId === userId) {
        await update(compRef, { currentUserId: null, isActive: false });
      }
    }
    // Delete user record
    await remove(userRef);
    return { success: true, message: 'המשתמש נמחק בהצלחה' };
  } catch (error) {
    logger.error('Error deleting user:', error);
    return { success: false, error: error.message || 'שגיאה במחיקת המשתמש' };
  }
};'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\userService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
