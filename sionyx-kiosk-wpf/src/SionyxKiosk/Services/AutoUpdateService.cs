using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Text;
using Serilog;

namespace SionyxKiosk.Services;

public static class AutoUpdateService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(AutoUpdateService));
    private const string UpdateServerUrl = "https://sionyx-auth-server.onrender.com/latest-version";
    private static string? _pendingUpdatePath = null;
    private static string? _pendingUpdateVersion = null;

    public static string? PendingUpdateVersion => _pendingUpdateVersion;
    public static bool HasPendingUpdate => _pendingUpdatePath != null && File.Exists(_pendingUpdatePath);

    /// <summary>Called on startup — downloads update in background if available.</summary>
    public static async Task CheckAndUpdateAsync(string currentVersion)
    {
        try
        {
            Logger.Information("[Update] Checking for updates (current: {Version})", currentVersion);
            using var http = new HttpClient();
            http.DefaultRequestHeaders.Add("User-Agent", "SIONYX-Kiosk");
            http.Timeout = TimeSpan.FromSeconds(10);

            var json = await http.GetStringAsync(UpdateServerUrl);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            var latestVersion = root.GetProperty("version").GetString() ?? "";
            var downloadUrl = root.GetProperty("downloadUrl").GetString() ?? "";

            if (string.IsNullOrEmpty(latestVersion) || string.IsNullOrEmpty(downloadUrl))
            {
                Logger.Information("[Update] No update info available");
                return;
            }

            if (!IsNewerVersion(latestVersion, currentVersion))
            {
                Logger.Information("[Update] Already up to date ({Version})", currentVersion);
                return;
            }

            Logger.Information("[Update] New version available: {Latest} (current: {Current})", latestVersion, currentVersion);

            // If no active session — install immediately
            if (!SessionStateService.HasActiveSession())
            {
                Logger.Information("[Update] No active session — installing immediately");
                await DownloadAndInstallAsync(downloadUrl, latestVersion, currentVersion);
                return;
            }

            // Active session — download in background, install after session ends
            Logger.Information("[Update] Active session detected — downloading in background");
            _ = Task.Run(async () => await DownloadInBackgroundAsync(downloadUrl, latestVersion));
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }
    }

    /// <summary>Check now and return result without installing.</summary>
    public static async Task<(bool hasUpdate, string latestVersion, string downloadUrl)> CheckForUpdateNowAsync(string currentVersion)
    {
        try
        {
            using var http = new HttpClient();
            http.DefaultRequestHeaders.Add("User-Agent", "SIONYX-Kiosk");
            http.Timeout = TimeSpan.FromSeconds(10);
            var json = await http.GetStringAsync(UpdateServerUrl);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            var latestVersion = root.GetProperty("version").GetString() ?? "";
            var downloadUrl = root.GetProperty("downloadUrl").GetString() ?? "";
            if (string.IsNullOrEmpty(latestVersion) || string.IsNullOrEmpty(downloadUrl))
                return (false, "", "");
            var hasUpdate = IsNewerVersion(latestVersion, currentVersion);
            return (hasUpdate, latestVersion, downloadUrl);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] CheckForUpdateNow failed");
            return (false, "", "");
        }
    }

    /// <summary>Force download and install immediately (called from tray menu).</summary>
    public static async Task ForceUpdateNowAsync(string currentVersion, Action<string>? statusCallback = null)
    {
        try
        {
            statusCallback?.Invoke("בודק עדכון...");
            var (hasUpdate, latestVersion, downloadUrl) = await CheckForUpdateNowAsync(currentVersion);
            if (!hasUpdate)
            {
                statusCallback?.Invoke("מעודכן לגרסה האחרונה");
                return;
            }
            statusCallback?.Invoke($"מוריד גרסה {latestVersion}...");
            await DownloadAndInstallAsync(downloadUrl, latestVersion, currentVersion);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Update] ForceUpdateNow failed");
            statusCallback?.Invoke("שגיאה בעדכון");
        }
    }

    /// <summary>Called by SessionCoordinator after session ends.</summary>
    public static async Task TryInstallPendingUpdateAsync()
    {
        if (!HasPendingUpdate) return;

        Logger.Information("[Update] Installing pending update {Version}", _pendingUpdateVersion);
        await InstallAsync(_pendingUpdatePath!, _pendingUpdateVersion ?? "");
    }

    // ==================== PRIVATE ====================

    private static async Task DownloadInBackgroundAsync(string downloadUrl, string version)
    {
        try
        {
            var tempPath = Path.Combine(AppContext.BaseDirectory, $"sionyx_update_{version}.msi");
            Logger.Information("[Update] Background download started: {Version}", version);

            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromMinutes(10);
            var bytes = await http.GetByteArrayAsync(downloadUrl);
            await File.WriteAllBytesAsync(tempPath, bytes);

            _pendingUpdatePath = tempPath;
            _pendingUpdateVersion = version;
            Logger.Information("[Update] Background download complete ({MB} MB) — will install after session", bytes.Length / 1024 / 1024);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Background download failed");
        }
    }

    private static async Task DownloadAndInstallAsync(string downloadUrl, string newVersion, string currentVersion)
    {
        try
        {
            var tempPath = Path.Combine(AppContext.BaseDirectory, $"sionyx_update_{newVersion}.msi");
            Logger.Information("[Update] Downloading {Url}", downloadUrl);

            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromMinutes(10);
            var bytes = await http.GetByteArrayAsync(downloadUrl);
            await File.WriteAllBytesAsync(tempPath, bytes);

            Logger.Information("[Update] Download complete ({MB} MB)", bytes.Length / 1024 / 1024);
            await InstallAsync(tempPath, newVersion);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Download+install failed");
        }
    }

    private static async Task InstallAsync(string msiPath, string version)
    {
        try
        {
            await LogUpdateToFirebase("installing", version);

            // Run via SIONYX_Update scheduled task (runs as SYSTEM)
            var taskResult = TryRunViaScheduledTask(msiPath);
            if (!taskResult)
            {
                // Fallback: direct msiexec (may fail without admin rights)
                Logger.Warning("[Update] Scheduled task failed, trying direct msiexec");
                var psi = new ProcessStartInfo
                {
                    FileName = "msiexec.exe",
                    Arguments = $"/i \"{msiPath}\" /quiet /norestart",
                    UseShellExecute = true,
                    Verb = "runas"
                };
                var proc = Process.Start(psi);
                proc?.WaitForExit(300000);
            }

            _pendingUpdatePath = null;
            _pendingUpdateVersion = null;
            await LogUpdateToFirebase("installed", version);
            Logger.Information("[Update] Install complete — restarting kiosk");

            // Restart kiosk only (no full machine restart)
            await Task.Delay(3000);
            var exePath = Process.GetCurrentProcess().MainModule?.FileName;
            if (!string.IsNullOrEmpty(exePath))
                Process.Start(new ProcessStartInfo(exePath) { UseShellExecute = true });

            System.Windows.Application.Current.Dispatcher.Invoke(() =>
                System.Windows.Application.Current.Shutdown());
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Update] Install failed");
            await LogUpdateToFirebase("failed", version);
        }
    }

    private static bool TryRunViaScheduledTask(string msiPath)
    {
        try
        {
            // Write MSI path to a known location for the scheduled task
            var triggerFile = Path.Combine(AppContext.BaseDirectory, "pending_update.txt");
            File.WriteAllText(triggerFile, msiPath);

            var psi = new ProcessStartInfo
            {
                FileName = "schtasks.exe",
                Arguments = "/run /tn \"SIONYX_Update\"",
                UseShellExecute = false,
                CreateNoWindow = true
            };
            var proc = Process.Start(psi);
            proc?.WaitForExit(5000);
            return proc?.ExitCode == 0;
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Could not run scheduled task");
            return false;
        }
    }

    private static async Task LogUpdateToFirebase(string status, string version)
    {
        try
        {
            var config = Infrastructure.FirebaseConfig.Load();
            var orgId = config.OrgId;
            var computerName = Environment.MachineName;
            var url = $"{config.DatabaseUrl}/organizations/{orgId}/computers/{computerName}/updateLog.json";

            var payload = new
            {
                status,
                version,
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                computerName
            };

            using var http = new HttpClient();
            var json = JsonSerializer.Serialize(payload);
            await http.PutAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
            Logger.Information("[Update] Logged to Firebase: {Status} v{Version}", status, version);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Failed to log update to Firebase");
        }
    }

    private static bool IsNewerVersion(string latest, string current)
    {
        try
        {
            return Version.Parse(latest) > Version.Parse(current);
        }
        catch
        {
            return string.Compare(latest, current, StringComparison.Ordinal) > 0;
        }
    }
}
