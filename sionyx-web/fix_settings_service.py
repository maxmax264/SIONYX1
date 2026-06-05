content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\settingsService.js', encoding='utf-8').read()
addition = '''
/**
 * Get phone verification requirement setting
 */
export const getPhoneVerificationSetting = async (orgId) => {
  try {
    const settingsRef = ref(database, `organizations/${orgId}/metadata/settings/requirePhoneVerification`);
    const snapshot = await get(settingsRef);
    return { success: true, requirePhoneVerification: snapshot.exists() ? snapshot.val() : false };
  } catch (error) {
    logger.error('Error getting phone verification setting:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Set phone verification requirement setting
 */
export const setPhoneVerificationSetting = async (orgId, value) => {
  try {
    const settingsRef = ref(database, `organizations/${orgId}/metadata/settings/requirePhoneVerification`);
    await update(ref(database, `organizations/${orgId}/metadata/settings`), { requirePhoneVerification: value });
    logger.info('Phone verification setting updated:', value);
    return { success: true };
  } catch (error) {
    logger.error('Error setting phone verification setting:', error);
    return { success: false, error: error.message };
  }
};
'''
content += addition
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\settingsService.js', 'w', encoding='utf-8').write(content)
print('OK')
