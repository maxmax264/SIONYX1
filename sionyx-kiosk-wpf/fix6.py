content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', encoding='utf-8').read()

new_content = """using Microsoft.Win32;
using Serilog;
using System.Diagnostics;

namespace SionyxKiosk.Services;

public static class KioskPolicyService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(KioskPolicyService));
    private const string PolicyKey = @"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer";

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
            key.SetValue("NoControlPanel", 1, RegistryValueKind.DWord);
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
}
"""

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', 'w', encoding='utf-8').write(new_content)
print('OK')
