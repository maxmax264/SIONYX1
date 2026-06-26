import { ref, get, update } from 'firebase/database';
import { database } from '../config/firebase';
import { logger } from '../utils/logger';

export const getPaymentSettings = async (orgId) => {
  try {
    const settingsRef = ref(database, `organizations/${orgId}/metadata/settings/payment`);
    const snapshot = await get(settingsRef);
    if (!snapshot.exists()) {
      return { success: true, payment: { saveCardEnabled: false, nedarimApiValid: '' } };
    }
    return { success: true, payment: snapshot.val() };
  } catch (error) {
    logger.error('Error getting payment settings:', error);
    return { success: false, error: error.message };
  }
};

export const updatePaymentSettings = async (orgId, payment) => {
  try {
    await update(ref(database, `organizations/${orgId}/metadata/settings`), {
      payment: {
        saveCardEnabled: !!payment.saveCardEnabled,
        nedarimApiValid: (payment.nedarimApiValid || '').trim(),
      },
    });
    logger.info('Payment settings updated');
    return { success: true };
  } catch (error) {
    logger.error('Error updating payment settings:', error);
    return { success: false, error: error.message };
  }
};
