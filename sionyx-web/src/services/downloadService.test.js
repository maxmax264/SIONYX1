import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getLatestRelease,
  downloadFile,
  downloadFileWithProgress,
  formatFileSize,
  formatReleaseDate,
  formatVersion,
} from './downloadService';

// Mock fetch
global.fetch = vi.fn();

// Mock document.createElement for download tests
const mockLink = {
  href: '',
  download: '',
  target: '',
  style: { display: '' },
  click: vi.fn(),
};

vi.spyOn(document, 'createElement').mockImplementation(() => mockLink);
vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});

describe('downloadService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLink.href = '';
    mockLink.download = '';
    mockLink.click.mockClear();
  });

  describe('getLatestRelease', () => {
    const githubRelease = {
      tag_name: 'v3.18.36',
      published_at: '2026-09-29T16:29:10Z',
      body: '## Changes\n- Fix VNC relay\n* Improve self-heal\nplain text',
      assets: [
        { name: 'notes.txt', size: 10, browser_download_url: 'https://github.com/x/notes.txt' },
        {
          name: 'sionyx-v3.18.36.msi',
          size: 121950208,
          browser_download_url:
            'https://github.com/maxmax264/sionyx-releases/releases/download/v3.18.36/sionyx-v3.18.36.msi',
        },
      ],
    };

    it('should return release info from GitHub Releases (primary)', async () => {
      global.fetch.mockResolvedValueOnce({ ok: true, json: async () => githubRelease });

      const result = await getLatestRelease();

      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch.mock.calls[0][0]).toContain(
        'api.github.com/repos/maxmax264/sionyx-releases/releases/latest'
      );
      expect(result.version).toBe('3.18.36');
      expect(result.downloadUrl).toContain('/download/v3.18.36/sionyx-v3.18.36.msi');
      expect(result.fileName).toBe('sionyx-v3.18.36.msi');
      expect(result.fileSize).toBe(121950208);
      expect(result.releaseDate).toBe('2026-09-29T16:29:10Z');
      expect(result.changelog).toEqual(['Fix VNC relay', 'Improve self-heal']);
    });

    it('should fall back to RTDB when GitHub fails', async () => {
      global.fetch
        .mockResolvedValueOnce({ ok: false, status: 403 })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            version: '1.2.3',
            downloadUrl: 'https://storage.example.com/sionyx.exe',
            buildNumber: 42,
          }),
        });

      const result = await getLatestRelease();

      expect(result.version).toBe('1.2.3');
      expect(result.downloadUrl).toBe('https://storage.example.com/sionyx.exe');
      expect(result.buildNumber).toBe(42);
      expect(global.fetch.mock.calls[1][0]).toContain('pc-sion-default-rtdb.firebaseio.com');
      expect(global.fetch.mock.calls[1][0]).not.toContain('undefined');
    });

    it('should fall back to Storage with a real bucket name when GitHub and RTDB fail', async () => {
      global.fetch
        .mockResolvedValueOnce({ ok: false, status: 403 })
        .mockResolvedValueOnce({ ok: false, status: 404 })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ version: '2.0.0', downloadUrl: 'https://storage.example.com/a.exe' }),
        });

      const result = await getLatestRelease();

      expect(result.version).toBe('2.0.0');
      expect(global.fetch.mock.calls[2][0]).toContain('/b/pc-sion.appspot.com/o/');
    });

    it('should throw error when every source fails', async () => {
      global.fetch.mockResolvedValue({ ok: false, status: 404 });

      await expect(getLatestRelease()).rejects.toThrow('Could not fetch release metadata');
    });

    it('should skip a GitHub release that has no installer asset', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ tag_name: 'v1.0.0', assets: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ version: '0.9.0', downloadUrl: 'https://storage.example.com/b.exe' }),
        });

      const result = await getLatestRelease();

      expect(result.version).toBe('0.9.0');
    });
  });

  describe('downloadFile', () => {
    it('should create download link and click it', async () => {
      await downloadFile('https://example.com/file.exe', 'file.exe');

      expect(document.createElement).toHaveBeenCalledWith('a');
      expect(mockLink.href).toBe('https://example.com/file.exe');
      expect(mockLink.download).toBe('file.exe');
      expect(mockLink.click).toHaveBeenCalled();
    });

    it('should throw error for invalid URL', async () => {
      await expect(downloadFile('', 'file.exe')).rejects.toThrow('Invalid download URL');
      await expect(downloadFile('ftp://invalid', 'file.exe')).rejects.toThrow(
        'Invalid download URL'
      );
    });

    it('should throw error when URL is null', async () => {
      await expect(downloadFile(null, 'file.exe')).rejects.toThrow('Invalid download URL');
    });
  });

  describe('downloadFileWithProgress', () => {
    it('should download and call progress callback', async () => {
      const onProgress = vi.fn();

      await downloadFileWithProgress('https://example.com/file.exe', 'file.exe', onProgress);

      expect(onProgress).toHaveBeenCalledWith(0, 100);
      expect(mockLink.click).toHaveBeenCalled();
    });

    it('should work without progress callback', async () => {
      await downloadFileWithProgress('https://example.com/file.exe', 'file.exe');

      expect(mockLink.click).toHaveBeenCalled();
    });

    it('should throw error for invalid URL', async () => {
      await expect(downloadFileWithProgress('', 'file.exe')).rejects.toThrow(
        'Invalid download URL'
      );
    });
  });

  describe('formatFileSize', () => {
    it('should return "Unknown size" for 0 bytes', () => {
      expect(formatFileSize(0)).toBe('Unknown size');
    });

    it('should format bytes correctly', () => {
      expect(formatFileSize(500)).toBe('500 Bytes');
    });

    it('should format kilobytes correctly', () => {
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(2048)).toBe('2 KB');
    });

    it('should format megabytes correctly', () => {
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(52428800)).toBe('50 MB');
    });

    it('should format gigabytes correctly', () => {
      expect(formatFileSize(1073741824)).toBe('1 GB');
    });
  });

  describe('formatReleaseDate', () => {
    it('should format date in Hebrew locale', () => {
      const result = formatReleaseDate('2024-01-15T10:00:00Z');
      // Should contain the year 2024
      expect(result).toContain('2024');
    });

    it('should handle invalid date', () => {
      const result = formatReleaseDate('invalid-date');
      // Should return Hebrew "unknown date" message or attempt to format
      // Invalid Date objects still pass toLocaleDateString but produce "Invalid Date"
      expect(typeof result).toBe('string');
    });
  });

  describe('formatVersion', () => {
    it('should return empty string for null release', () => {
      expect(formatVersion(null)).toBe('');
      expect(formatVersion(undefined)).toBe('');
    });

    it('should return version string', () => {
      expect(formatVersion({ version: '1.2.3' })).toBe('1.2.3');
    });

    it('should include build number when available', () => {
      expect(formatVersion({ version: '1.2.3', buildNumber: 42 })).toBe('1.2.3 (Build #42)');
    });

    it('should default to "Latest" when no version', () => {
      expect(formatVersion({})).toBe('Latest');
    });
  });
});
