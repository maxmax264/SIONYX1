using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Checks GitHub Releases for a newer version and installs it silently.
/// Only runs when no client session is active.
/// </summary>
public static class AutoUpdateService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(AutoUpdateService));
    private const string UpdateServerUrl = "https://sionyx-auth-server.onrender.com/latest-version";

    public static async Task CheckAndUpdateAsync(string currentVersion)
    {
        try
        {
            // Never update during an active client session
            if (SessionStateService.HasActiveSession())
            {
                Logger.Information("[Update] Skipping update check - active session");
                return;
            }

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

            Logger.Information("[Update] Latest version: {Latest}", latestVersion);

            if (!IsNewerVersion(latestVersion, currentVersion))
            {
                Logger.Information("[Update] Already up to date");
                return;
            }

            Logger.Information("[Update] New version available: {Latest} (current: {Current})", latestVersion, currentVersion);

            // Download MSI
            var tempPath = Path.Combine(Path.GetTempPath(), $"sionyx_update_{latestVersion}.msi");
            Logger.Information("[Update] Downloading {Url} to {Path}", downloadUrl, tempPath);

            var msiBytes = await http.GetByteArrayAsync(downloadUrl);
            await File.WriteAllBytesAsync(tempPath, msiBytes);

            Logger.Information("[Update] Download complete ({Size} MB), installing...", msiBytes.Length / 1024 / 1024);

            // Install silently
            var psi = new ProcessStartInfo
            {
                FileName = "msiexec.exe",
                Arguments = $"/i \"{tempPath}\" /quiet /norestart",
                UseShellExecute = false,
                CreateNoWindow = true
            };
            var proc = Process.Start(psi);
            proc?.WaitForExit(300000); // 5 min timeout

            Logger.Information("[Update] Install complete (exit={Code})", proc?.ExitCode);

            // Cleanup temp file
            try { File.Delete(tempPath); } catch { }
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }
    }

    private static bool IsNewerVersion(string latest, string current)
    {
        try
        {
            var l = Version.Parse(latest);
            var c = Version.Parse(current);
            return l > c;
        }
        catch
        {
            return string.Compare(latest, current, StringComparison.Ordinal) > 0;
        }
    }
}
