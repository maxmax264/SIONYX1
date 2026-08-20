import { database } from '../config/firebase';
import { ref, get } from 'firebase/database';
import { logger } from '../utils/logger';

/**
 * Base URL of the Render bridge server that now hosts registerOrganization
 * (moved off Firebase Cloud Functions, which require the Blaze plan).
 */
const BRIDGE_BASE_URL = (
  import.meta.env.VITE_PAYMENT_BRIDGE_URL || 'https://sionyx-payment-bridge.onrender.com'
).replace(/\/$/, '');

/**
 * Organization Service
 *
 * This service handles organization-related operations including:
 * - Registration of new organizations
 * - Retrieving organization metadata (including NEDARIM credentials)
 * - Getting organization statistics for the admin dashboard
 */

const decodeData = encodedData => {
  try {
    return JSON.parse(atob(encodedData));
  } catch (error) {
    logger.error('Error decoding data:', error);
    return null;
  }
};

// New encryption format used by Cloud Function (base64 encoded JSON)
const decodeCloudFunctionData = encodedData => {
  try {
    // The Cloud Function uses Buffer.from(JSON.stringify(data)).toString('base64')
    // So we need to decode it back
    const jsonString = atob(encodedData);
    return JSON.parse(jsonString);
  } catch (error) {
    logger.error('Error decoding Cloud Function data:', error);
    return null;
  }
};

/**
 * Register a new organization via the Render bridge server
 *
 * WHY NEEDED: Landing page needs this to register new organizations
 * with their NEDARIM credentials for payment processing
 *
 * @param {Object} organizationData - Organization details including NEDARIM credentials
 * @returns {Object} Success status and organization ID
 */
export const registerOrganization = async organizationData => {
  try {
    logger.info('Calling Render bridge for organization registration:', {
      hasData: !!organizationData,
    });

    const response = await fetch(`${BRIDGE_BASE_URL}/registerOrganization`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: organizationData }),
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      const message =
        (payload && payload.error && payload.error.message) || 'Registration failed';
      logger.error('Registration failed:', { status: response.status, message });
      return { success: false, error: message };
    }

    const result = (payload && payload.result) || payload || {};
    logger.info('Organization registered successfully:', result);
    return result;
  } catch (error) {
    logger.error('Error calling registration server:', error);
    return {
      success: false,
      error: 'Failed to register organization. Please try again.',
    };
  }
};

/**
 * Get organization metadata including NEDARIM credentials
 *
 * WHY NEEDED: Python client needs this to fetch NEDARIM credentials
 * from database instead of environment variables for payment processing
 *
 * @param {string} orgId - Organization ID
 * @returns {Object} Success status and decoded metadata
 */
export const getOrganizationMetadata = async orgId => {
  try {
    const orgRef = ref(database, `organizations/${orgId}/metadata`);
    const snapshot = await get(orgRef);

    if (snapshot.exists()) {
      const data = snapshot.val();

      // Try both decoding methods for backward compatibility
      let decodedMosadId, decodedApiValid;

      try {
        // Try new Cloud Function format first
        decodedMosadId = decodeCloudFunctionData(data.nedarim_mosad_id);
        decodedApiValid = decodeCloudFunctionData(data.nedarim_api_valid);
      } catch {
        // Fall back to old format
        decodedMosadId = decodeData(data.nedarim_mosad_id);
        decodedApiValid = decodeData(data.nedarim_api_valid);
      }

      return {
        success: true,
        metadata: {
          ...data,
          nedarim_mosad_id: decodedMosadId,
          nedarim_api_valid: decodedApiValid,
        },
      };
    } else {
      return {
        success: false,
        error: 'Organization not found',
      };
    }
  } catch (error) {
    logger.error('Error getting organization metadata:', error);
    return {
      success: false,
      error: 'Failed to get organization metadata',
    };
  }
};

/**
 * Get organization statistics for admin dashboard
 *
 * WHY NEEDED: OverviewPage needs this to display dashboard statistics
 * including user count, package count, purchases, revenue, and time metrics
 *
 * @param {string} orgId - Organization ID
 * @returns {Object} Success status and statistics data
 */
export const getOrganizationStats = async orgId => {
  try {
    // Get users count
    const usersRef = ref(database, `organizations/${orgId}/users`);
    const usersSnapshot = await get(usersRef);
    const usersCount = usersSnapshot.exists() ? Object.keys(usersSnapshot.val()).length : 0;

    // Get packages count
    const packagesRef = ref(database, `organizations/${orgId}/packages`);
    const packagesSnapshot = await get(packagesRef);
    const packagesCount = packagesSnapshot.exists()
      ? Object.keys(packagesSnapshot.val()).length
      : 0;

    // Get purchases count and total revenue
    const purchasesRef = ref(database, `organizations/${orgId}/purchases`);
    const purchasesSnapshot = await get(purchasesRef);

    let purchasesCount = 0;
    let totalRevenue = 0;
    let totalTimeMinutes = 0;
    const packageDistribution = {};
    const purchasesRaw = [];

    if (purchasesSnapshot.exists()) {
      const purchasesData = purchasesSnapshot.val();
      purchasesCount = Object.keys(purchasesData).length;

      Object.values(purchasesData).forEach(purchase => {
        if (purchase.status === 'completed' && purchase.amount) {
          totalRevenue += parseFloat(purchase.amount) || 0;
        }
        if (purchase.minutes) {
          totalTimeMinutes += parseInt(purchase.minutes) || 0;
        }
        const pkgName = purchase.packageName || 'אחר';
        packageDistribution[pkgName] = (packageDistribution[pkgName] || 0) + 1;

        purchasesRaw.push({
          id: purchase.id,
          amount: purchase.amount,
          createdAt: purchase.createdAt,
          status: purchase.status,
          packageName: purchase.packageName || null,
          minutes: purchase.minutes,
          type: purchase.type,
          note: purchase.note,
          userId: purchase.userId,
          timeSeconds: purchase.timeSeconds,
          prints: purchase.prints,
        });
      });
    }

    return {
      success: true,
      stats: {
        usersCount,
        packagesCount,
        purchasesCount,
        totalRevenue,
        totalTimeMinutes,
        packageDistribution,
        purchases: purchasesRaw,
      },
    };
  } catch (error) {
    logger.error('Error getting organization stats:', error);
    return {
      success: false,
      error: 'Failed to get organization statistics',
    };
  }
};
