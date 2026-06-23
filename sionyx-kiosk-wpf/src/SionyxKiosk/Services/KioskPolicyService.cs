using Microsoft.Win32;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Applies and removes Windows Registry policies for kiosk mode.
/// Currently manages: NoControlPanel (blocks Control Panel and PC Settings).
/// </summary>
public static class KioskPolicyService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(KioskPolicyService));
    private const string PolicyKey = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";

    public static void Apply()
    {
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(PolicyKey, writable: true);
            key.SetValue("NoControlPanel", 1, RegistryValueKind.DWord);
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
                Logger.Information("[KioskPolicy] NoControlPanel removed");
            }
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[KioskPolicy] Failed to remove NoControlPanel");
        }
    }

    /// <summary>
    /// Temporarily removes the policy, runs the action, then restores.
    /// </summary>
    public static void RunWithControlPanel(Action action)
    {
        Remove();
        try { action(); }
        finally { Apply(); }
    }
}
