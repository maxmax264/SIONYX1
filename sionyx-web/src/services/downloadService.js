/**
 * Download Service for SIONYX
 * ===========================
 * Handles downloading of SIONYX installers with automatic version discovery.
 * Primary source: GitHub Releases of maxmax264/sionyx-releases (public repo).
 * Fallbacks: Firebase RTDB (public/latestRelease), then Firebase Storage (latest.json).
 */

import { logger } from '../utils/logger';

const GITHUB_LATEST_RELEASE_URL =
  'https://api.github.com/repos/maxmax264/sionyx-releases/releases/latest';

// Same values as config/firebase.js - used when the VITE_ env vars are not set at build time
const DEFAULT_STORAGE_BUCKET = 'pc-sion.appspot.com';
const DEFAULT_DATABASE_URL = 'https://pc-sion-default-rtdb.firebaseio.com';

/**
 * Get Firebase Storage bucket from environment or default
 */
const getStorageBucket = () => {
  return import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || DEFAULT_STORAGE_BUCKET;
};

/**
 * Build a Firebase Storage REST API URL for a given path.
 * Uses the firebasestorage.googleapis.com endpoint which respects
 * Firebase Security Rules (unlike storage.googleapis.com which needs IAM/ACL).
 */
const getFirebaseStorageUrl = path => {
  const bucket = getStorageBucket();
  const encodedPath = encodeURIComponent(path);
  return `https://firebasestorage.googleapis.com/v0/b/${bucket}/o/${encodedPath}`;
};

/**
 * Get Firebase RTDB URL for public data
 */
const getRtdbUrl = path => {
  const databaseUrl = import.meta.env.VITE_FIREBASE_DATABASE_URL || DEFAULT_DATABASE_URL;
  return `${databaseUrl}/${path}.json`;
};

/**
 * Extract changelog bullet lines from a GitHub release body (markdown)
 */
const parseChangelog = body => {
  if (!body) return [];
  return body
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => /^[-*]\s+/.test(line))
    .map(line => line.replace(/^[-*]\s+/, ''));
};

/**
 * Fetch the latest release from GitHub Releases (sionyx-releases repo)
 * and map it to the same metadata shape the rest of the service expects.
 * @returns {Promise<Object|null>} Release metadata, or null if unavailable
 */
const fetchGithubLatestMetadata = async () => {
  try {
    const response = await fetch(GITHUB_LATEST_RELEASE_URL, {
      headers: { Accept: 'application/vnd.github+json' },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`GitHub responded with ${response.status}`);
    }

    const release = await response.json();
    const assets = Array.isArray(release?.assets) ? release.assets : [];
    const asset =
      assets.find(a => /\.msi$/i.test(a.name)) || assets.find(a => /\.exe$/i.test(a.name));

    if (!asset || !asset.browser_download_url) {
      throw new Error('No installer asset found in latest release');
    }

    logger.info('Release metadata loaded from GitHub Releases');
    return {
      version: String(release.tag_name || '').replace(/^v/i, '') || undefined,
      downloadUrl: asset.browser_download_url,
      releaseDate: release.published_at,
      fileSize: asset.size,
      filename: asset.name,
      changelog: parseChangelog(release.body),
    };
  } catch (error) {
    logger.warn('GitHub releases fetch failed, trying Firebase fallback:', error.message);
    return null;
  }
};

/**
 * Fetch the latest release metadata.
 *
 * Primary: GitHub Releases (maxmax264/sionyx-releases)
 *   - Public repo, CORS-enabled, same source build.ps1 publishes to
 *
 * Fallback 1: Firebase Realtime Database (public/latestRelease)
 *   - No auth needed, no Storage 403 issues
 *
 * Fallback 2: Firebase Storage (latest.json)
 *   - May fail with 403 if uniform bucket-level access is enabled
 *
 * @returns {Promise<Object>} Release metadata
 */
const fetchLatestMetadata = async () => {
  // PRIMARY: GitHub Releases
  const githubData = await fetchGithubLatestMetadata();
  if (githubData) return githubData;

  // FALLBACK 1: Fetch from RTDB
  try {
    const rtdbUrl = `${getRtdbUrl('public/latestRelease')}?t=${Date.now()}`;
    const response = await fetch(rtdbUrl, { cache: 'no-store' });

    if (response.ok) {
      const data = await response.json();
      if (data && data.downloadUrl) {
        logger.info('Release metadata loaded from RTDB');
        return data;
      }
    }
  } catch (error) {
    logger.warn('RTDB fetch failed, trying Storage fallback:', error.message);
  }

  // FALLBACK 2: Fetch from Firebase Storage
  try {
    const cacheBuster = `t=${Date.now()}`;
    const metadataUrl = `${getFirebaseStorageUrl('latest.json')}?alt=media&${cacheBuster}`;

    const response = await fetch(metadataUrl, { cache: 'no-store' });

    if (!response.ok) {
      throw new Error(`Failed to fetch metadata: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    logger.warn('Could not fetch latest.json metadata:', error.message);
    return null;
  }
};

/**
 * Get the latest release information from Firebase Storage metadata
 * @returns {Promise<Object>} Release information including download URL
 */
export const getLatestRelease = async () => {
  const metadata = await fetchLatestMetadata();

  if (metadata && metadata.downloadUrl) {
    return {
      version: metadata.version || 'Latest',
      downloadUrl: metadata.downloadUrl,
      releaseDate: metadata.releaseDate || new Date().toISOString(),
      fileSize: metadata.fileSize || 0,
      fileName: metadata.filename || `sionyx-installer-v${metadata.version}.exe`,
      buildNumber: metadata.buildNumber || null,
      changelog: metadata.changelog || [],
    };
  }

  throw new Error('Could not fetch release metadata. Please try again later.');
};

/**
 * Get all available versions (if version history is enabled)
 * @returns {Promise<Array>} List of available versions
 */
export const getAvailableVersions = async () => {
  // For now, just return latest version
  // Could be extended to list all versions from storage
  const latest = await getLatestRelease();
  return [latest];
};

/**
 * Download a file from a URL
 * @param {string} url - The download URL
 * @param {string} filename - The filename to save as
 * @returns {Promise<void>}
 */
export const downloadFile = async (url, filename) => {
  try {
    logger.info(`Starting download: ${filename} from ${url}`);

    if (!url || !url.startsWith('http')) {
      throw new Error('Invalid download URL');
    }

    // Direct download approach (CORS-friendly)
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    logger.info(`Download initiated: ${filename}`);
  } catch (error) {
    logger.error('Download failed:', error);
    throw new Error(`Download failed: ${error.message}`);
  }
};

/**
 * Download with progress tracking
 * @param {string} url - Download URL
 * @param {string} filename - Filename
 * @param {Function} onProgress - Progress callback (loaded, total)
 * @returns {Promise<void>}
 */
export const downloadFileWithProgress = async (url, filename, onProgress) => {
  try {
    logger.info(`Starting download: ${filename}`);

    if (!url || !url.startsWith('http')) {
      throw new Error('Invalid download URL');
    }

    // Simulate progress for direct download
    if (onProgress) onProgress(0, 100);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    if (onProgress) setTimeout(() => onProgress(100, 100), 100);

    logger.info(`Download initiated: ${filename}`);
  } catch (error) {
    logger.error('Download failed:', error);
    throw new Error(`Download failed: ${error.message}`);
  }
};

/**
 * Format file size in human readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Human readable file size
 */
export const formatFileSize = bytes => {
  if (bytes === 0) return 'Unknown size';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Format release date
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatReleaseDate = dateString => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return 'תאריך לא ידוע';
  }
};

/**
 * Format version string for display
 * @param {Object} release - Release object
 * @returns {string} Formatted version string
 */
export const formatVersion = release => {
  if (!release) return '';

  let version = release.version || 'Latest';
  if (release.buildNumber) {
    version += ` (Build #${release.buildNumber})`;
  }

  return version;
};
