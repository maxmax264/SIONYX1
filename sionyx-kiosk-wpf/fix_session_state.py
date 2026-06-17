new_content = """using Microsoft.Win32;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Manages kiosk session state in Registry.
/// Survives power outages — on next boot, kiosk detects and cleans up stale sessions.
/// </summary>
public static class SessionStateService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(SessionStateService));
    private const string SessionKey = @"SOFTWARE\\SIONYX\\Session";

    // ── Write ────────────────────────────────────────────────────────

    public static void SetSessionActive(string userId)
    {
        try
        {
            using var key = Registry.LocalMachine.CreateSubKey(SessionKey, writable: true);
            if (key == null) return;
            key.SetValue("ActiveSession",  1,                              RegistryValueKind.DWord);
            key.SetValue("CurrentUser",    userId,                         RegistryValueKind.String);
            key.SetValue("SessionStart",   DateTime.UtcNow.ToString("o"), RegistryValueKind.String);
            key.SetValue("EnteredDesktop", 0,                              RegistryValueKind.DWord);
            Logger.Information("[Session] Session started for user {UserId}", userId);
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] SetSessionActive failed"); }
    }

    public static void SetEnteredDesktop(bool entered)
    {
        try
        {
            using var key = Registry.LocalMachine.CreateSubKey(SessionKey, writable: true);
            key?.SetValue("EnteredDesktop", entered ? 1 : 0, RegistryValueKind.DWord);
            Logger.Information("[Session] EnteredDesktop = {Value}", entered);
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] SetEnteredDesktop failed"); }
    }

    public static void ClearSession()
    {
        try
        {
            using var key = Registry.LocalMachine.CreateSubKey(SessionKey, writable: true);
            if (key == null) return;
            key.SetValue("ActiveSession",  0,  RegistryValueKind.DWord);
            key.SetValue("EnteredDesktop", 0,  RegistryValueKind.DWord);
            key.SetValue("CurrentUser",    "", RegistryValueKind.String);
            Logger.Information("[Session] Session cleared");
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] ClearSession failed"); }
    }

    // ── Read ─────────────────────────────────────────────────────────

    public static bool HasActiveSession()
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(SessionKey);
            if (key == null) return false;
            return (int)(key.GetValue("ActiveSession") ?? 0) == 1;
        }
        catch { return false; }
    }

    public static bool HasEnteredDesktop()
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(SessionKey);
            if (key == null) return false;
            return (int)(key.GetValue("EnteredDesktop") ?? 0) == 1;
        }
        catch { return false; }
    }

    public static string? GetCurrentUser()
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(SessionKey);
            return key?.GetValue("CurrentUser")?.ToString();
        }
        catch { return null; }
    }
}
"""

path = r'.\\src\\SionyxKiosk\\Services\\SessionStateService.cs'
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("DONE")
