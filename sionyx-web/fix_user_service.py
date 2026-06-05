content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\userService.js', encoding='utf-8').read()
addition = '''
/**
 * Manually verify a user phone (admin override)
 */
export const verifyUserPhone = async (orgId, userId) => {
  try {
    const userRef = ref(database, `organizations/${orgId}/users/${userId}`);
    await update(userRef, {
      phoneVerified: true,
      phoneVerifiedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    return { success: true };
  } catch (error) {
    logger.error('Error verifying user phone:', error);
    return { success: false, error: error.message };
  }
};
'''
content += addition
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\userService.js', 'w', encoding='utf-8').write(content)
print('OK')
