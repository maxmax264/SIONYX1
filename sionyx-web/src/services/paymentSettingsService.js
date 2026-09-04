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

const encodeBillingValue = (value) => {
  try {
    return btoa(JSON.stringify(value || ""));
  } catch {
    return btoa(JSON.stringify(""));
  }
};

export const getBillingSettings = async (orgId) => {
  try {
    const metadataRef = ref(database, `organizations/${orgId}/metadata`);
    const snapshot = await get(metadataRef);
    if (!snapshot.exists()) {
      return { success: false, error: 'Organization not found' };
    }
    const data = snapshot.val();
    let nedarimMosadId = '';
    let nedarimApiValid = '';
    try {
      nedarimMosadId = JSON.parse(atob(data.nedarim_mosad_id || '')) || '';
    } catch {
      // Missing/invalid stored value - leave nedarimMosadId as default ''
    }
    try {
      nedarimApiValid = JSON.parse(atob(data.nedarim_api_valid || '')) || '';
    } catch {
      // Missing/invalid stored value - leave nedarimApiValid as default ''
    }
    return {
      success: true,
      billing: {
        nedarimMosadId,
        nedarimApiValid,
        billingConfigured: !!data.billing_configured,
      },
    };
  } catch (error) {
    logger.error('Error getting billing settings:', error);
    return { success: false, error: error.message };
  }
};

export const updateBillingSettings = async (orgId, billing) => {
  try {
    const cleanMosadId = (billing.nedarimMosadId || '').trim();
    const cleanApiValid = (billing.nedarimApiValid || '').trim();
    const billingConfigured = !!(cleanMosadId && cleanApiValid);
    await update(ref(database, `organizations/${orgId}/metadata`), {
      nedarim_mosad_id: encodeBillingValue(cleanMosadId),
      nedarim_api_valid: encodeBillingValue(cleanApiValid),
      billing_configured: billingConfigured,
    });
    logger.info('Billing settings updated');
    return { success: true, billingConfigured };
  } catch (error) {
    logger.error('Error updating billing settings:', error);
    return { success: false, error: error.message };
  }
};
