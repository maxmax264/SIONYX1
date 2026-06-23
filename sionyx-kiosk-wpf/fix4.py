content = """using Microsoft.Win32;
using Serilog;
using System.Runtime.InteropServices;

namespace SionyxKiosk.Services;

/// <summary>
/// Applies and removes Windows Registry policies for kiosk mode.
/// Currently manages: NoControlPanel (blocks Control Panel and PC Settings).
/// </summary>
public static class KioskPolicyService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(KioskPolicyService));
    private const string PolicyKey = @"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer";

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr SendMessageTimeout(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam,
        uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);

    private static readonly IntPtr HWND_BROADCAST = new IntPtr(0xFFFF);
    private const uint WM_SETTINGCHANGE = 0x001A;
    private const uint SMTO_ABORTIFHUNG = 0x0002;

    private static void NotifyWindows()
    {
        SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero,
            "Policy", SMTO_ABORTIFHUNG, 1000, out _);
    }

    public static void Apply()
    {
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(PolicyKey, writable: true);
            key.SetValue("NoControlPanel", 1, RegistryValueKind.DWord);
            NotifyWindows();
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
                NotifyWindows();
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
"""
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', 'w', encoding='utf-8').write(content)
print('OK')
