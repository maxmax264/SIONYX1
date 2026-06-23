using System.Diagnostics;


using System.IO;


using System.Net.Http;


using System.Text.Json;


using System.Text;


using System.Timers;


using Serilog;





namespace SionyxKiosk.Services;





public static class AutoUpdateService


{


    private static readonly ILogger Logger = Log.ForContext(typeof(AutoUpdateService));


    private const string UpdateServerUrl = "https://sionyx-auth-server.onrender.com/latest-version";


    private static string? _pendingUpdatePath = null;


    private static string? _pendingUpdateVersion = null;


    private static System.Timers.Timer? _periodicTimer = null;


    private static string? _currentVersion = null;


    private static volatile bool _isCheckInProgress = false;


    private static DateTime _lastInstallAttemptUtc = DateTime.MinValue;


    private static readonly TimeSpan InstallCooldown = TimeSpan.FromMinutes(2);





    // Progress events — UI subscribes to these


    public static event Action<string>? UpdateStarted;   // version


    public static event Action<int, string>? ProgressChanged; // percent, status


    public static event Action? UpdateCompleted;





    public static string? PendingUpdateVersion => _pendingUpdateVersion;


    public static bool HasPendingUpdate => _pendingUpdatePath != null && File.Exists(_pendingUpdatePath);





    /// <summary>Called on startup — checks for updates and starts periodic check.</summary>


    public static async Task CheckAndUpdateAsync(string currentVersion)


    {


        if (_isCheckInProgress) return;


        _isCheckInProgress = true;


        _currentVersion = currentVersion;


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





            if (!SessionStateService.HasActiveSession())


            {


                Logger.Information("[Update] No active session — installing immediately");


                await DownloadAndInstallAsync(downloadUrl, latestVersion, currentVersion);


                return;


            }





            Logger.Information("[Update] Active session detected — downloading in background");


            _ = Task.Run(async () => await DownloadInBackgroundAsync(downloadUrl, latestVersion));


        }


        catch (Exception ex)


        {


            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");


        }


        finally


        {


            _isCheckInProgress = false;





            // Start (or restart) the periodic timer here, in `finally`, so it


            // always runs exactly once after every check — regardless of


            // whether the check exited early via `return` (e.g. "no active


            // session, installing immediately"). Previously this call lived


            // after the try/finally block and was skipped by those early


            // returns, so the periodic timer effectively never started in


            // any session where an update was installed.


            ApplyIntervalFromRegistry();


        }


    }





    /// <summary>Read interval from registry and (re)start the periodic timer. Default: 1 minute.</summary>


    public static void ApplyIntervalFromRegistry()


    {


        _periodicTimer?.Stop();


        _periodicTimer?.Dispose();


        _periodicTimer = null;





        var raw = Infrastructure.RegistryConfig.ReadValueCurrentUser("UpdateCheckIntervalMinutes");


        // Default to 1 minute if not set


        if (!int.TryParse(raw, out var minutes))


            minutes = 1;





        if (minutes <= 0)


        {


            Logger.Information("[Update] Periodic check disabled");


            return;


        }





        Logger.Information("[Update] Periodic check every {Minutes} min", minutes);


        _periodicTimer = new System.Timers.Timer(minutes * 60_000);


        _periodicTimer.Elapsed += async (_, _) =>


        {


            if (_currentVersion != null)


                await CheckAndUpdateAsync(_currentVersion);


        };


        _periodicTimer.AutoReset = true;


        _periodicTimer.Start();


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


            var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{version}_{DateTime.UtcNow.Ticks}.msi");


            Logger.Information("[Update] Background download started: {Version}", version);


            using var http = new HttpClient();


            http.Timeout = TimeSpan.FromMinutes(10);


            using var response = await http.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);
            response.EnsureSuccessStatusCode();
            var expectedBytes = response.Content.Headers.ContentLength ?? 0;
            using (var fs = new FileStream(tempPath, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                await response.Content.CopyToAsync(fs);
            }
            var actualBytes = new FileInfo(tempPath).Length;
            if (expectedBytes > 0 && actualBytes < expectedBytes)
            {
                File.Delete(tempPath);
                Logger.Warning("[Update] Background download incomplete ({Actual} of {Expected} bytes) - deleted", actualBytes, expectedBytes);
                return;
            }


            var triggerFile = Path.Combine(GetUpdateFolder(), "pending_update.txt");
            File.WriteAllText(triggerFile, tempPath, System.Text.Encoding.ASCII);
            Logger.Information("[Update] Background download complete ({MB} MB) - trigger file written", actualBytes / 1024 / 1024);


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


            UpdateStarted?.Invoke(newVersion);


            ProgressChanged?.Invoke(0, "מתחיל הורדה...");





            var tempPath = Path.Combine(GetUpdateFolder(), $"sionyx_update_{newVersion}_{DateTime.UtcNow.Ticks}.msi");


            Logger.Information("[Update] Downloading {Url}", downloadUrl);





            using var http = new HttpClient(new HttpClientHandler { AllowAutoRedirect = true });


            http.Timeout = TimeSpan.FromMinutes(10);





            using var response = await http.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);


            var totalBytes = response.Content.Headers.ContentLength ?? 0;


            Logger.Information("[Update] Download size: {Bytes} bytes (Content-Length={CL})", totalBytes, response.Content.Headers.ContentLength);


            var buffer = new byte[81920];


            var downloaded = 0L;





            await using var stream = await response.Content.ReadAsStreamAsync();


            await using var fileStream = File.Create(tempPath);





            int read;


            while ((read = await stream.ReadAsync(buffer)) > 0)


            {


                await fileStream.WriteAsync(buffer.AsMemory(0, read));


                downloaded += read;


                if (totalBytes > 0)


                {


                    var percent = (int)(downloaded * 100 / totalBytes);


                    var mb = downloaded / 1024.0 / 1024.0;


                    var totalMb = totalBytes / 1024.0 / 1024.0;


                    ProgressChanged?.Invoke(percent, $"מוריד... {mb:F1} / {totalMb:F1} MB");


                }


            }





            Logger.Information("[Update] Download complete ({MB} MB)", downloaded / 1024 / 1024);



            // Verify downloaded file size matches expected

            var fileInfo = new FileInfo(tempPath);

            if (totalBytes > 0 && fileInfo.Length != totalBytes)

            {

                Logger.Error("[Update] Size mismatch: expected {Expected}, got {Actual} — deleting corrupt file", totalBytes, fileInfo.Length);

                try { File.Delete(tempPath); } catch { }

                await LogUpdateToFirebase("failed", newVersion);

                return;

            }

            Logger.Information("[Update] Download verified OK: {Bytes} bytes", fileInfo.Length);

            ProgressChanged?.Invoke(90, "מתקין עדכון...");


            await InstallAsync(tempPath, newVersion);


        }


        catch (Exception ex)


        {


            Logger.Warning(ex, "[Update] Download+install failed");


        }


    }





    private static async Task InstallAsync(string msiPath, string version)


    {


        var sinceLastAttempt = DateTime.UtcNow - _lastInstallAttemptUtc;


        if (sinceLastAttempt < InstallCooldown)


        {


            Logger.Information("[Update] Skipping install attempt — cooldown active ({Remaining}s remaining)", (int)(InstallCooldown - sinceLastAttempt).TotalSeconds);


            return;


        }


        _lastInstallAttemptUtc = DateTime.UtcNow;





        try


        {


            await LogUpdateToFirebase("installing", version);





            var written = TryRunViaScheduledTask(msiPath);


            if (!written)


            {


                Logger.Warning("[Update] Could not write trigger file — aborting install, will retry next periodic check");


                await LogUpdateToFirebase("failed", version);


                return;


            }





            ProgressChanged?.Invoke(92, "ממתין למשימה להתקין...");





            // Poll the registry for up to 90 seconds to confirm the scheduled task


            // actually installed the MSI before declaring success. Without this wait,


            // the kiosk would restart immediately, still see the old version, and


            // re-download/re-install in an infinite loop.


            var installed = await WaitForRegistryVersionAsync(version, msiPath, TimeSpan.FromMinutes(5));





            if (!installed)


            {


                Logger.Warning("[Update] Install did not complete within timeout — will retry on next periodic check (no immediate retry)");


                await LogUpdateToFirebase("timeout", version);


                ProgressChanged?.Invoke(95, "ההתקנה מתעכבת, ממתין...");


                // Do not restart the kiosk and do not clear pending state here;


                // the next periodic timer tick will re-check the real installed


                // version from the registry and decide whether to retry.


                return;


            }





            _pendingUpdatePath = null;


            _pendingUpdateVersion = null;


            await LogUpdateToFirebase("installed", version);


            Logger.Information("[Update] Install confirmed via registry — restarting kiosk");





            UpdateCompleted?.Invoke();


            // Stop the periodic timer explicitly. Application.Shutdown() does
            // NOT stop a running System.Timers.Timer, so without this the old
            // process can keep "ticking" in the background even after a new
            // process has been started, causing duplicate downloads/installs.
            _periodicTimer?.Stop();
            _periodicTimer?.Dispose();
            var exePath = Process.GetCurrentProcess().MainModule?.FileName;
            if (!string.IsNullOrEmpty(exePath))
                Process.Start(new ProcessStartInfo(exePath, "--kiosk") { UseShellExecute = true });
            System.Windows.Application.Current.Dispatcher.Invoke(() =>
                System.Windows.Application.Current.Shutdown());


        }


        catch (Exception ex)


        {


            Logger.Error(ex, "[Update] Install failed");


            await LogUpdateToFirebase("failed", version);


        }


    }





    /// <summary>


    /// Polls HKLM\SOFTWARE\SIONYX\Version every 2 seconds until it matches the


    /// expected version or the timeout elapses. The MSI (run by the SYSTEM


    /// scheduled task) writes this registry value on successful install.


    /// </summary>


    private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, string msiPath, TimeSpan timeout)


    {


        var deadline = DateTime.UtcNow + timeout;


        var attempt = 0;


        while (DateTime.UtcNow < deadline)


        {


            attempt++;


            // Re-write trigger file every poll so the scheduled task always


            // has it, even if a previous run deleted it before msiexec finished.


            try


            {


                var tf = Path.Combine(GetUpdateFolder(), "pending_update.txt");


                File.WriteAllText(tf, msiPath);


                Logger.Information("[Update] Poll #{Attempt}: trigger file re-written to {Path}", attempt, tf);


            }


            catch (Exception tfEx)


            {


                Logger.Warning("[Update] Poll #{Attempt}: could not write trigger file: {Err}", attempt, tfEx.Message);


            }


            var current = GetInstalledVersion();


            Logger.Information("[Update] Registry poll #{Attempt}: current='{Current}' expected='{Expected}'", attempt, current ?? "(null)", expectedVersion);





            if (!string.IsNullOrEmpty(current) && string.Equals(current.Trim(), expectedVersion.Trim(), StringComparison.OrdinalIgnoreCase))


            {


                Logger.Information("[Update] Registry version matched on poll #{Attempt}", attempt);


                return true;


            }





            await Task.Delay(2000);


        }


        Logger.Warning("[Update] Registry poll timed out after {Attempts} attempts", attempt);


        return false;


    }




    private static string? GetInstalledVersion()
    {
        try
        {
            var uninstallKey = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall";
            using var key = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(uninstallKey);
            if (key == null) { Logger.Warning("[Update] GetInstalledVersion: Uninstall key not found"); return null; }
            foreach (var subName in key.GetSubKeyNames())
            {
                using var sub = key.OpenSubKey(subName);
                var name = sub?.GetValue("DisplayName")?.ToString();
                var version = sub?.GetValue("DisplayVersion")?.ToString();
                if (name == "SIONYX")
                {
                    Logger.Information("[Update] GetInstalledVersion: found SIONYX version={Version} in key={Key}", version, subName);
                    return version;
                }
            }
            // Also check WOW6432Node
            var uninstallKey32 = @"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall";
            using var key32 = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(uninstallKey32);
            if (key32 != null)
            {
                foreach (var subName in key32.GetSubKeyNames())
                {
                    using var sub = key32.OpenSubKey(subName);
                    var name = sub?.GetValue("DisplayName")?.ToString();
                    var version = sub?.GetValue("DisplayVersion")?.ToString();
                    if (name == "SIONYX")
                    {
                        Logger.Information("[Update] GetInstalledVersion: found SIONYX version={Version} in WOW key={Key}", version, subName);
                        return version;
                    }
                }
            }
            Logger.Warning("[Update] GetInstalledVersion: SIONYX not found in registry");
            return null;
        }
        catch (Exception ex) { Logger.Warning("[Update] GetInstalledVersion exception: {Ex}", ex.Message); return null; }
    }


    private static bool TryRunViaScheduledTask(string msiPath)


    {


        try


        {


            // Write trigger file to C:\Windows\Temp — SIONYX_Update scheduled task


            // runs every minute as SYSTEM and picks it up automatically


            var triggerFile = Path.Combine(GetUpdateFolder(), "pending_update.txt");


            File.WriteAllText(triggerFile, msiPath, System.Text.Encoding.ASCII);


            Logger.Information("[Update] Trigger file written — waiting for scheduled task to pick up");


            // Also trigger the task directly in case the time trigger is disabled
            try
            {
                var psi = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "schtasks.exe",
                    Arguments = "/run /tn \"SIONYX_Update\"",
                    UseShellExecute = true,
                    Verb = "open",
                    CreateNoWindow = true,
                    WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden
                };
                System.Diagnostics.Process.Start(psi);
                Logger.Information("[Update] Scheduled task triggered directly");
            }
            catch (Exception taskEx)
            {
                Logger.Warning("[Update] Could not trigger task directly: {Err}", taskEx.Message);
            }
            return true;


        }


        catch (Exception ex)


        {


            Logger.Warning(ex, "[Update] Could not write trigger file");


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


            var payload = new { status, version, timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), computerName };


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


        try { return Version.Parse(latest) > Version.Parse(current); }


        catch { return string.Compare(latest, current, StringComparison.Ordinal) > 0; }


    }





    /// <summary>


    /// Returns a writable folder for staging the downloaded MSI and the


    /// trigger file that the SYSTEM scheduled task reads. C:\Windows\Temp


    /// was tried first but some machines have non-standard ACLs on it that


    /// silently truncate writes for regular (non-admin) users. This folder


    /// (under Public Documents) grants Modify to INTERACTIVE users and Full


    /// Control to SYSTEM by default on every Windows install, so it is safe


    /// across machines without any manual ACL changes.


    /// </summary>


    private static string GetUpdateFolder()


    {


        var folder = Path.Combine(@"C:\Users\Public\Documents\SIONYX", "updates");


        Directory.CreateDirectory(folder);


        CleanupOldMsiFiles(folder);


        return folder;


    }





    /// <summary>


    /// Deletes leftover .msi files older than 10 minutes from the update


    /// folder. Each download now uses a unique filename (version + ticks),


    /// so without this cleanup the folder would accumulate a new ~67MB file


    /// on every install attempt forever. Files newer than 10 minutes are


    /// left alone in case a scheduled task run is still reading one.


    /// </summary>


    private static void CleanupOldMsiFiles(string folder)


    {


        try


        {


            foreach (var file in Directory.GetFiles(folder, "sionyx_update_*.msi"))


            {


                try


                {


                    var info = new FileInfo(file);


                    if (DateTime.UtcNow - info.LastWriteTimeUtc > TimeSpan.FromMinutes(10))


                        info.Delete();


                }


                catch


                {


                    // File may be in use by msiexec right now; skip it silently,


                    // it will be picked up by a later cleanup pass.


                }


            }


        }


        catch (Exception ex)


        {


            Logger.Warning(ex, "[Update] Could not clean up old MSI files");


        }


    }


}

















