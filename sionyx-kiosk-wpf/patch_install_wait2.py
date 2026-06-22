import re

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_install = '''    private static async Task InstallAsync(string msiPath, string version)
    {
        try
        {
            await LogUpdateToFirebase("installing", version);
            var taskResult = TryRunViaScheduledTask(msiPath);
            _pendingUpdatePath = null;
            _pendingUpdateVersion = null;
            await LogUpdateToFirebase("installed", version);
            Logger.Information("[Update] Install complete \u2014 restarting kiosk");
            UpdateCompleted?.Invoke();
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
    }'''

new_install = '''    private static async Task InstallAsync(string msiPath, string version)
    {
        try
        {
            await LogUpdateToFirebase("installing", version);

            var written = TryRunViaScheduledTask(msiPath);
            if (!written)
            {
                Logger.Warning("[Update] Could not write trigger file \u2014 aborting install, will retry next periodic check");
                await LogUpdateToFirebase("failed", version);
                return;
            }

            ProgressChanged?.Invoke(92, "\u05de\u05de\u05ea\u05d9\u05df \u05dc\u05de\u05e9\u05d9\u05de\u05d4 \u05dc\u05d4\u05ea\u05e7\u05d9\u05df...");

            // Poll the registry for up to 90 seconds to confirm the scheduled task
            // actually installed the MSI before declaring success. Without this wait,
            // the kiosk would restart immediately, still see the old version, and
            // re-download/re-install in an infinite loop.
            var installed = await WaitForRegistryVersionAsync(version, TimeSpan.FromSeconds(90));

            if (!installed)
            {
                Logger.Warning("[Update] Install did not complete within timeout \u2014 will retry on next periodic check (no immediate retry)");
                await LogUpdateToFirebase("timeout", version);
                ProgressChanged?.Invoke(95, "\u05d4\u05d4\u05ea\u05e7\u05e0\u05d4 \u05de\u05ea\u05e2\u05db\u05d1\u05ea, \u05de\u05de\u05ea\u05d9\u05df...");
                // Do not restart the kiosk and do not clear pending state here;
                // the next periodic timer tick will re-check the real installed
                // version from the registry and decide whether to retry.
                return;
            }

            _pendingUpdatePath = null;
            _pendingUpdateVersion = null;
            await LogUpdateToFirebase("installed", version);
            Logger.Information("[Update] Install confirmed via registry \u2014 restarting kiosk");

            UpdateCompleted?.Invoke();
            await Task.Delay(1500);
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

    /// <summary>
    /// Polls HKLM\\SOFTWARE\\SIONYX\\Version every 2 seconds until it matches the
    /// expected version or the timeout elapses. The MSI (run by the SYSTEM
    /// scheduled task) writes this registry value on successful install.
    /// </summary>
    private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, TimeSpan timeout)
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

count = content.count(old_install)
if count == 0:
    print("ERROR: Target not found.")
elif count > 1:
    print(f"ERROR: Target found {count} times, expected exactly 1. Aborting.")
else:
    content = content.replace(old_install, new_install)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched successfully!")
