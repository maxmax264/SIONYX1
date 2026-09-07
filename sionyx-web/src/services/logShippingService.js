import { ref, get, set } from 'firebase/database';
import { database } from '../config/firebase';
import { logger } from '../utils/logger';

/**
 * Multi-site log shipping (Stage 7). Every kiosk in the org ships its live
 * log stream to whichever destination(s) are configured here - each with
 * its own URL, API key, and frequency, controllable without a kiosk restart.
 *
 * Stored at: organizations/{orgId}/logShipping/destinations/{destinationId}
 *   { label, url, apiKey, intervalMs, enabled }
 */

export const getLogShippingDestinations = async (orgId) => {
  try {
    const destRef = ref(database, `organizations/${orgId}/logShipping/destinations`);
    const snapshot = await get(destRef);
    if (!snapshot.exists()) return { success: true, destinations: [] };
    const data = snapshot.val();
    const destinations = Object.entries(data).map(([id, d]) => ({
      id,
      label: d.label || id,
      url: d.url || '',
      apiKey: d.apiKey || '',
      intervalMs: typeof d.intervalMs === 'number' ? d.intervalMs : 0,
      enabled: d.enabled !== false,
    }));
    return { success: true, destinations };
  } catch (error) {
    logger.error('Error getting log-shipping destinations:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Replaces the full destination list (this is a full overwrite, matching
 * the "menu with options" UX - the dashboard always sends the whole
 * current list, not a partial patch, so removed sites actually disappear).
 */
export const saveLogShippingDestinations = async (orgId, destinations) => {
  try {
    for (const d of destinations) {
      if (!d.url || !d.url.trim()) {
        return { success: false, error: 'כל אתר חייב כתובת URL' };
      }
    }
    const payload = {};
    destinations.forEach((d, index) => {
      const id = d.id || `site${index + 1}`;
      payload[id] = {
        label: d.label || id,
        url: d.url.trim(),
        apiKey: d.apiKey || '',
        intervalMs: Number(d.intervalMs) || 0,
        enabled: !!d.enabled,
      };
    });
    await set(ref(database, `organizations/${orgId}/logShipping/destinations`), payload);
    logger.info('Log-shipping destinations saved:', Object.keys(payload));
    return { success: true };
  } catch (error) {
    logger.error('Error saving log-shipping destinations:', error);
    return { success: false, error: error.message };
  }
};
