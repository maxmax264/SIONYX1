path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ---------------------------------------------------------------------------
# Fix 1: Stop the periodic timer BEFORE restarting/shutting down, and force
# a hard process exit as a fallback. Application.Current.Shutdown() does not
# stop a running System.Timers.Timer, so the old process can stay alive as a
# "zombie" whose timer keeps firing every minute and re-triggering downloads
# in parallel with the new process that was just started. This was the real
# cause of the repeated download/install loop even after WaitForRegistryVersionAsync
# was added.
# ---------------------------------------------------------------------------
old_restart_block = '''            UpdateCompleted?.Invoke();
            await Task.Delay(1500);
            var exePath = Process.GetCurrentProcess().MainModule?.FileName;
            if (!string.IsNullOrEmpty(exePath))
                Process.Start(new ProcessStartInfo(exePath) { UseShellExecute = true });

            System.Windows.Application.Current.Dispatcher.Invoke(() =>
                System.Windows.Application.Current.Shutdown());'''

new_restart_block = '''            UpdateCompleted?.Invoke();
            await Task.Delay(1500);

            // Stop the periodic timer explicitly. Application.Shutdown() does
            // NOT stop a running System.Timers.Timer, so without this the old
            // process can keep "ticking" in the background even after a new
            // process has been started, causing duplicate downloads/installs.
            _periodicTimer?.Stop();
            _periodicTimer?.Dispose();
            _periodicTimer = null;

            var exePath = Process.GetCurrentProcess().MainModule?.FileName;
            if (!string.IsNullOrEmpty(exePath))
                Process.Start(new ProcessStartInfo(exePath) { UseShellExecute = true });

            System.Windows.Application.Current.Dispatcher.Invoke(() =>
                System.Windows.Application.Current.Shutdown());

            // Hard fallback: if Shutdown() does not fully terminate the
            // process (e.g. background threads keep it alive), force exit
            // after a short grace period so no zombie instance survives.
            await Task.Delay(3000);
            Environment.Exit(0);'''

count = content.count(old_restart_block)
if count == 1:
    content = content.replace(old_restart_block, new_restart_block)
    changes += 1
    print("Fix 1 applied: timer stop + hard exit fallback.")
else:
    print(f"Fix 1 NOT applied (found {count} occurrences, expected 1).")

# ---------------------------------------------------------------------------
# Fix 2: Add detailed per-attempt logging inside WaitForRegistryVersionAsync
# so the next time this happens we see exactly what the registry contained
# at each poll, instead of guessing from indirect evidence.
# ---------------------------------------------------------------------------
old_wait = '''    private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, TimeSpan timeout)
    {
        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            var current = Infrastructure.RegistryConfig.ReadValue("Version");
            if (!string.IsNullOrEmpty(current) && string.Equals(current.Trim(), expectedVersion.Trim(), StringComparison.OrdinalIgnoreCase))
                return true;

            await Task.Delay(2000);
        }
        return false;
    }'''

new_wait = '''    private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, TimeSpan timeout)
    {
        var deadline = DateTime.UtcNow + timeout;
        var attempt = 0;
        while (DateTime.UtcNow < deadline)
        {
            attempt++;
            var current = Infrastructure.RegistryConfig.ReadValue("Version");
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
    }'''

count = content.count(old_wait)
if count == 1:
    content = content.replace(old_wait, new_wait)
    changes += 1
    print("Fix 2 applied: detailed registry poll logging.")
else:
    print(f"Fix 2 NOT applied (found {count} occurrences, expected 1).")

# ---------------------------------------------------------------------------
# Fix 3: Add a cooldown safety net. Even with fixes 1 and 2, add a minimum
# gap between install attempts so that if anything else goes wrong, the
# system cannot hammer downloads more than once per cooldown window.
# ---------------------------------------------------------------------------
old_field_block = '''    private static System.Timers.Timer? _periodicTimer = null;
    private static string? _currentVersion = null;
    private static volatile bool _isCheckInProgress = false;'''

new_field_block = '''    private static System.Timers.Timer? _periodicTimer = null;
    private static string? _currentVersion = null;
    private static volatile bool _isCheckInProgress = false;
    private static DateTime _lastInstallAttemptUtc = DateTime.MinValue;
    private static readonly TimeSpan InstallCooldown = TimeSpan.FromMinutes(2);'''

count = content.count(old_field_block)
if count == 1:
    content = content.replace(old_field_block, new_field_block)
    changes += 1
    print("Fix 3a applied: cooldown fields added.")
else:
    print(f"Fix 3a NOT applied (found {count} occurrences, expected 1).")

old_install_start = '''    private static async Task InstallAsync(string msiPath, string version)
    {
        try
        {
            await LogUpdateToFirebase("installing", version);'''

new_install_start = '''    private static async Task InstallAsync(string msiPath, string version)
    {
        var sinceLastAttempt = DateTime.UtcNow - _lastInstallAttemptUtc;
        if (sinceLastAttempt < InstallCooldown)
        {
            Logger.Information("[Update] Skipping install attempt \u2014 cooldown active ({Remaining}s remaining)", (int)(InstallCooldown - sinceLastAttempt).TotalSeconds);
            return;
        }
        _lastInstallAttemptUtc = DateTime.UtcNow;

        try
        {
            await LogUpdateToFirebase("installing", version);'''

count = content.count(old_install_start)
if count == 1:
    content = content.replace(old_install_start, new_install_start)
    changes += 1
    print("Fix 3b applied: cooldown check in InstallAsync.")
else:
    print(f"Fix 3b NOT applied (found {count} occurrences, expected 1).")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal changes applied: {changes} of 4 expected.")
