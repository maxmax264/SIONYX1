/**
 * Computer Management Service for Admin Dashboard
 * Handles computer/PC tracking and management
 */

import { ref, get, set, update, remove } from 'firebase/database';
import { database } from '../config/firebase';
import { getOrgId } from '../hooks/useOrgId';
import { logger } from '../utils/logger';

/**
 * Get all computers in the organization
 */
export const getAllComputers = async () => {
  try {
    // Get organization ID from localStorage or user data
    const orgId = getOrgId();
    const computersRef = ref(database, `organizations/${orgId}/computers`);
    const snapshot = await get(computersRef);

    if (snapshot.exists()) {
      const computers = snapshot.val();
      const computerList = Object.keys(computers).map(computerId => ({
        id: computerId,
        ...computers[computerId],
      }));

      return {
        success: true,
        data: computerList,
      };
    } else {
      return {
        success: true,
        data: [],
      };
    }
  } catch (error) {
    logger.error('Error fetching computers:', error);
    return {
      success: false,
      error: 'Failed to fetch computers',
    };
  }
};

/**
 * Get computer usage statistics
 */
export const getComputerUsageStats = async () => {
  try {
    // Get all computers
    const computersResult = await getAllComputers();
    if (!computersResult.success) {
      return computersResult;
    }

    const computers = computersResult.data;

    // Get all users
    const orgId = getOrgId();
    const usersRef = ref(database, `organizations/${orgId}/users`);
    const usersSnapshot = await get(usersRef);
    const users = usersSnapshot.exists() ? usersSnapshot.val() : {};

    // Process statistics
    const stats = {
      totalComputers: computers.length,
      activeComputers: 0,
      computersWithUsers: 0,
      computerDetails: [],
      userComputerUsage: {},
    };

    computers.forEach(computer => {
      const currentUserId = computer.currentUserId;
      const isActive = computer.isActive || !!currentUserId;

      if (isActive) {
        stats.activeComputers++;
      }

      if (currentUserId) {
        stats.computersWithUsers++;

        // Get user info
        const userData = users[currentUserId] || {};
        const userName = `${userData.firstName || ''} ${userData.lastName || ''}`.trim();

        stats.computerDetails.push({
          computerId: computer.id,
          computerName: computer.computerName || 'Unknown',
          location: computer.location || '',
          isActive: isActive,
          currentUserId: currentUserId,
          currentUserName: userName,
          lastSeen: computer.lastSeen || '',
          osInfo: computer.osInfo || {},
          macAddress: computer.macAddress || '',
          ipAddress: computer.networkInfo?.local_ip || '',
        });

        // Track user's computer usage
        if (!stats.userComputerUsage[currentUserId]) {
          stats.userComputerUsage[currentUserId] = {
            userId: currentUserId,
            userName: userName,
            computersUsed: [],
          };
        }

        stats.userComputerUsage[currentUserId].computersUsed.push({
          computerId: computer.id,
          computerName: computer.computerName || 'Unknown',
          loginTime: computer.lastUserLogin || '',
        });
      } else {
        // Computer without user
        stats.computerDetails.push({
          computerId: computer.id,
          computerName: computer.computerName || 'Unknown',
          location: computer.location || '',
          isActive: isActive,
          currentUserId: null,
          currentUserName: null,
          lastSeen: computer.lastSeen || '',
          osInfo: computer.osInfo || {},
          macAddress: computer.macAddress || '',
          ipAddress: computer.networkInfo?.local_ip || '',
        });
      }
    });

    return {
      success: true,
      data: stats,
    };
  } catch (error) {
    logger.error('Error getting computer usage stats:', error);
    return {
      success: false,
      error: 'Failed to get computer usage statistics',
    };
  }
};

/**
 * Derive activeUsers and stats from computers and users arrays (for real-time updates)
 * @param {Array} computers - Array of { id, ...computerData }
 * @param {Array} usersArray - Array of { uid, ...userData }
 * @returns {{ activeUsers: Array, stats: Object }}
 */
export const deriveFromComputersAndUsers = (computers, usersArray) => {
  const users = {};
  (usersArray || []).forEach(u => {
    users[u.uid] = u;
  });

  const stats = {
    totalComputers: computers.length,
    activeComputers: 0,
    computersWithUsers: 0,
    computerDetails: [],
    userComputerUsage: {},
  };
  const activeUsers = [];

  (computers || []).forEach(computer => {
    const computerId = computer.id;
    const currentUserId = computer.currentUserId;
    const isActive = computer.isActive || !!currentUserId;

    if (isActive) stats.activeComputers++;
    if (currentUserId) stats.computersWithUsers++;

    const userData = users[currentUserId] || {};
    const userName = `${userData.firstName || ''} ${userData.lastName || ''}`.trim();

    if (currentUserId) {
      activeUsers.push({
        userId: currentUserId,
        userName,
        userPhone: userData.phoneNumber || '',
        computerId,
        computerName: computer.computerName || 'Unknown',
        computerLocation: computer.location || '',
        loginTime: computer.lastUserLogin || '',
        sessionStartTime: userData.sessionStartTime || null,
        sessionActive: userData.isSessionActive || false,
        remainingTime: userData.remainingTime || 0,
        printBalance: userData.printBalance || 0,
      });

      stats.computerDetails.push({
        computerId,
        computerName: computer.computerName || 'Unknown',
        location: computer.location || '',
        isActive,
        currentUserId,
        currentUserName: userName,
        lastSeen: computer.lastSeen || '',
        osInfo: computer.osInfo || {},
        macAddress: computer.macAddress || '',
        ipAddress: computer.networkInfo?.local_ip || '',
      });

      if (!stats.userComputerUsage[currentUserId]) {
        stats.userComputerUsage[currentUserId] = {
          userId: currentUserId,
          userName,
          computersUsed: [],
        };
      }
      stats.userComputerUsage[currentUserId].computersUsed.push({
        computerId,
        computerName: computer.computerName || 'Unknown',
        loginTime: computer.lastUserLogin || '',
      });
    } else {
      stats.computerDetails.push({
        computerId,
        computerName: computer.computerName || 'Unknown',
        location: computer.location || '',
        isActive,
        currentUserId: null,
        currentUserName: null,
        lastSeen: computer.lastSeen || '',
        osInfo: computer.osInfo || {},
        macAddress: computer.macAddress || '',
        ipAddress: computer.networkInfo?.local_ip || '',
      });
    }
  });

  return { activeUsers, stats };
};

/**
 * Get computer by ID
 */
export const getComputerById = async computerId => {
  try {
    const orgId = getOrgId();
    const computerRef = ref(database, `organizations/${orgId}/computers/${computerId}`);
    const snapshot = await get(computerRef);

    if (snapshot.exists()) {
      return {
        success: true,
        data: {
          id: computerId,
          ...snapshot.val(),
        },
      };
    } else {
      return {
        success: false,
        error: 'Computer not found',
      };
    }
  } catch (error) {
    logger.error('Error fetching computer:', error);
    return {
      success: false,
      error: 'Failed to fetch computer',
    };
  }
};

/**
 * Update computer information
 */
export const updateComputer = async (computerId, updates) => {
  try {
    const orgId = getOrgId();
    const computerRef = ref(database, `organizations/${orgId}/computers/${computerId}`);

    // Add updatedAt timestamp
    const updateData = {
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    await update(computerRef, updateData);

    return {
      success: true,
    };
  } catch (error) {
    logger.error('Error updating computer:', error);
    return {
      success: false,
      error: 'Failed to update computer',
    };
  }
};

/**
 * Delete computer
 */
export const deleteComputer = async computerId => {
  try {
    const orgId = getOrgId();
    const computerRef = ref(database, `organizations/${orgId}/computers/${computerId}`);
    await remove(computerRef);

    return {
      success: true,
    };
  } catch (error) {
    logger.error('Error deleting computer:', error);
    return {
      success: false,
      error: 'Failed to delete computer',
    };
  }
};

/** Asks a kiosk to re-report its current RustDesk ID+password to Firebase.
 * Covers a failed initial report or an ID/password that changed (e.g. reinstall).
 * The kiosk's RemoteControlReportingService listens for this in real time and
 * re-reports within seconds - no need to touch the machine. */
export const requestRemoteControlRefresh = async computerId => {
  try {
    const orgId = getOrgId();
    await update(ref(database, `organizations/${orgId}/computers/${computerId}/remoteControl`), { refreshRequested: Date.now() });
    return { success: true };
  } catch (error) {
    logger.error('Error requesting remote-control refresh:', error);
    return { success: false, error: 'Failed to request refresh' };
  }
};

/** Push a new AnyDesk password for a specific kiosk. Written to the `setPassword`
 * command channel (separate from `password`, which the kiosk itself uses to
 * self-report its currently-installed password). The kiosk's
 * RemoteControlReportingService picks this up in real time (SseListener) and
 * applies it via `AnyDesk.exe --set-password` - no reboot needed.
 * Requires org-admin role (enforced by database.rules.json on this path). */
export const setAnyDeskPassword = async (computerId, password) => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/remoteControl/anydesk/setPassword`), password);
    return { success: true };
  } catch (error) {
    logger.error('Error setting AnyDesk password:', error);
    return { success: false, error: 'Failed to set AnyDesk password' };
  }
};

/** Ask a kiosk to launch TeamViewer QuickSupport on demand (not installed as an
 * always-on unattended service - this is intentional, see install-teamviewer.ps1
 * header: a permanently-listening Host is what TeamViewer's free-tier commercial-use
 * detection flags across a fleet). The kiosk's RemoteControlReportingService listens
 * for this flag, launches the staged TeamViewerQS.exe, reads the freshly-generated
 * ID+password from tvinfo.ini, reports them back, and clears the flag. The ID is
 * normally stable per machine; the password is randomized by TeamViewer on every
 * launch, so this must be called again each time before connecting. */
export const requestTeamViewerLaunch = async computerId => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/remoteControl/teamviewer/launchRequest`), Date.now());
    return { success: true };
  } catch (error) {
    logger.error('Error requesting TeamViewer launch:', error);
    return { success: false, error: 'Failed to request TeamViewer launch' };
  }
};

/** Master-dashboard "send logs from every kiosk now" button (Stage 4). Writes
 * to an org-wide (not per-computer) path - every kiosk's LogShippingControlService
 * listens on the same path, so this one write fans out to the whole fleet.
 * Each kiosk posts its current log file to the entertainment-channel site,
 * tagged with its own name, independent of the always-on live stream. */
export const requestLogShipTriggerAll = async () => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/logShipping/triggerAllRequested`), Date.now());
    return { success: true };
  } catch (error) {
    logger.error('Error requesting fleet-wide log ship:', error);
    return { success: false, error: 'Failed to trigger log shipping' };
  }
};

/** Per-kiosk "send log" button (Stage 5) - same idea as requestLogShipTriggerAll
 * but scoped to a single computer, via `computers/{id}/logShipping/triggerRequested`. */
export const requestLogShipTrigger = async computerId => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/logShipping/triggerRequested`), Date.now());
    return { success: true };
  } catch (error) {
    logger.error('Error requesting per-kiosk log ship:', error);
    return { success: false, error: 'Failed to trigger log shipping' };
  }
};

/** Stage 6 - dashboard's live control over how often each kiosk ships a log
 * line to the channel (ChannelLogSink's throttle). Applied by every kiosk
 * immediately via a real-time listener - no restart needed. `ms = 0` means
 * "ship every line immediately" (the current default for active development). */
export const setLogShipIntervalMs = async ms => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/logShipping/intervalMs`), ms);
    return { success: true };
  } catch (error) {
    logger.error('Error setting log-shipping interval:', error);
    return { success: false, error: 'Failed to set log-shipping interval' };
  }
};

/** Ask a kiosk to shut down or restart now (or a graceful, delayed variant).
 * Written to `computers/{id}/powerCommand/requested` - the kiosk's new
 * RemoteCommandService listens for this in real time (SseListener, same
 * pattern as RustDesk/AnyDesk/log-shipping) and runs Windows `shutdown.exe`,
 * then reports back to `powerCommand/lastResult` and clears `requested`.
 * Admin-only, enforced by database.rules.json on this path. */
export const requestPowerCommand = async (computerId, type) => {
  try {
    const orgId = getOrgId();
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/powerCommand/requested`), {
      type, // 'shutdown' | 'restart'
      requestedAt: Date.now(),
    });
    return { success: true };
  } catch (error) {
    logger.error('Error requesting power command:', error);
    return { success: false, error: 'Failed to send power command' };
  }
};

/** Open a VNC remote-control session for a kiosk.
 * Generates a one-time random token, writes it to
 * `computers/{id}/vncRelay/requested` for the kiosk's VncRelayService to
 * pick up (bridges its local TightVNC to the sionyx-vnc-relay WebSocket
 * relay), and returns a ready-to-open noVNC viewer URL using that same
 * token. Admin-only, enforced by database.rules.json on this path.
 *
 * VNC_RELAY_BASE_URL below must point at the deployed sionyx-vnc-relay
 * Render service (separate repo, separate Render service from this app
 * and from the Understood payment bridge). */
const VNC_RELAY_BASE_URL = 'https://sionyx-vnc-relay.onrender.com'; // TODO: update after deploying sionyx-vnc-relay on Render

export const requestVncSession = async computerId => {
  try {
    const orgId = getOrgId();
    const token = crypto.getRandomValues(new Uint32Array(4)).join('');
    await set(ref(database, `organizations/${orgId}/computers/${computerId}/vncRelay/requested`), {
      token,
      requestedAt: Date.now(),
    });
    return { success: true, viewerUrl: `${VNC_RELAY_BASE_URL}/vnc.html?token=${token}` };
  } catch (error) {
    logger.error('Error requesting VNC session:', error);
    return { success: false, error: 'Failed to start VNC session' };
  }
};

/**
 * Get users currently using computers
 */
export const getActiveComputerUsers = async () => {
  try {
    const computersResult = await getAllComputers();
    if (!computersResult.success) {
      return computersResult;
    }

    const computers = computersResult.data;
    const activeUsers = [];

    for (const computer of computers) {
      if (computer.currentUserId) {
        // Get user details
        const orgId = getOrgId();
        const userRef = ref(database, `organizations/${orgId}/users/${computer.currentUserId}`);
        const userSnapshot = await get(userRef);

        if (userSnapshot.exists()) {
          const userData = userSnapshot.val();
          activeUsers.push({
            userId: computer.currentUserId,
            userName: `${userData.firstName || ''} ${userData.lastName || ''}`.trim(),
            userPhone: userData.phoneNumber || '',
            computerId: computer.id,
            computerName: computer.computerName || 'Unknown',
            computerLocation: computer.location || '',
            loginTime: computer.lastUserLogin || '',
            sessionStartTime: userData.sessionStartTime || null,
            sessionActive: userData.isSessionActive || false,
            remainingTime: userData.remainingTime || 0,
            printBalance: userData.printBalance || 0,
          });
        }
      }
    }

    return {
      success: true,
      data: activeUsers,
    };
  } catch (error) {
    logger.error('Error getting active computer users:', error);
    return {
      success: false,
      error: 'Failed to get active computer users',
    };
  }
};

/**
 * Force logout user from computer
 * This is a full logout - clears session, computer association, AND login status
 */
export const forceLogoutUser = async (userId, computerId) => {
  try {
    // Clear user's current computer and mark as logged out
    const orgId = getOrgId();
    const userRef = ref(database, `organizations/${orgId}/users/${userId}`);
    await update(userRef, {
      currentComputerId: null,
      currentComputerName: null,
      isSessionActive: false,
      isLoggedIn: false, // User is now logged out
      sessionStartTime: null,
      lastComputerLogout: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });

    // Clear computer's current user and mark as inactive
    const computerRef = ref(database, `organizations/${orgId}/computers/${computerId}`);
    await update(computerRef, {
      currentUserId: null,
      lastUserLogout: new Date().toISOString(),
      isActive: false,
      updatedAt: new Date().toISOString(),
    });

    return {
      success: true,
    };
  } catch (error) {
    logger.error('Error forcing logout:', error);
    return {
      success: false,
      error: 'Failed to force logout user',
    };
  }
};
