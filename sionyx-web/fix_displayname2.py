content = open(r'.\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()
old = """import { ref, get, push, set } from 'firebase/database';
import { database } from '../../config/firebase';"""
new = """import { ref, get, push, set, update } from 'firebase/database';
import { database } from '../../config/firebase';

export const getSupervisorDisplayName = async (supervisorId) => {
  try {
    const snap = await get(ref(database, `supervisors/${supervisorId}/displayName`));
    return { success: true, displayName: snap.exists() ? snap.val() : '' };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const updateSupervisorDisplayName = async (supervisorId, displayName) => {
  try {
    await update(ref(database, `supervisors/${supervisorId}`), { displayName: displayName.trim() });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
