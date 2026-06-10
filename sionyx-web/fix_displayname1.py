content = open(r'.\src\services\settingsService.js', encoding='utf-8').read()
old = """/**
 * Get phone verification requirement setting
 */"""
new = """/**
 * Get display name for messages (shown in kiosk)
 */
export const getDisplayName = async (orgId) => {
  try {
    const nameRef = ref(database, `organizations/${orgId}/metadata/settings/displayName`);
    const snapshot = await get(nameRef);
    return { success: true, displayName: snapshot.exists() ? snapshot.val() : '' };
  } catch (error) {
    logger.error('Error getting display name:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Update display name for messages (shown in kiosk)
 */
export const updateDisplayName = async (orgId, displayName) => {
  try {
    await update(ref(database, `organizations/${orgId}/metadata/settings`), { displayName: displayName.trim() });
    logger.info('Display name updated:', displayName);
    return { success: true };
  } catch (error) {
    logger.error('Error updating display name:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get phone verification requirement setting
 */"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\settingsService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
