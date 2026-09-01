using Microsoft.Win32;
using Serilog;
using System.Diagnostics;

namespace SionyxKiosk.Services;

public static class KioskPolicyService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(KioskPolicyService));
    private const string PolicyKey = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";

    private static void RestartExplorer()
    {
        try
        {
            foreach (var p in Process.GetProcessesByName("explorer"))
                p.Kill();
            System.Threading.Thread.Sleep(500);
            Process.Start("explorer.exe");
            Logger.Information("[KioskPolicy] Explorer restarted");
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[KioskPolicy] Failed to restart explorer");
        }
    }

    public static void Apply()
    {
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(PolicyKey, writable: true);

            // Killing and restarting explorer.exe is what makes the real desktop
            // briefly flash on screen (even under a Topmost window) - it's the
            // shell process being torn down and rebuilt. Only worth doing when
            // the policy is actually changing; every login was calling Apply()
            // unconditionally and restarting explorer even when NoControlPanel
            // was already set from a previous session on the same Windows user.
            var alreadyApplied = key.GetValue("NoControlPanel") is int existing && existing == 1;

            key.SetValue("NoControlPanel", 1, RegistryValueKind.DWord);

            if (!alreadyApplied)
                RestartExplorer();

            Logger.Information("[KioskPolicy] NoControlPanel applied");
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[KioskPolicy] Failed to apply NoControlPanel");
        }
    }

    public static void Remove()
    {
        try
        {
            using var key = Registry.CurrentUser.OpenSubKey(PolicyKey, writable: true);
            if (key?.GetValue("NoControlPanel") != null)
            {
                key.DeleteValue("NoControlPanel");
                RestartExplorer();
                Logger.Information("[KioskPolicy] NoControlPanel removed");
            }
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[KioskPolicy] Failed to remove NoControlPanel");
        }
    }

    public static void RunWithControlPanel(Action action)
    {
        Remove();
        try { action(); }
        finally { Apply(); }
    }

    public static async System.Threading.Tasks.Task RunWithControlPanelAsync()
    {
        Remove();
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = "shell:::{26EE0668-A00A-44D7-9371-BEB064C98683}",
                UseShellExecute = true
            });
            await System.Threading.Tasks.Task.Run(() =>
                System.Windows.MessageBox.Show(
                    "לוח הבקרה פתוח.\nלחץ אישור לאחר שתסיים — המערכת תינעל חזרה.",
                    "SIONYX — מצב מנהל",
                    System.Windows.MessageBoxButton.OK,
                    System.Windows.MessageBoxImage.Information));
        }
        finally
        {
            Apply();
        }
    }
}
