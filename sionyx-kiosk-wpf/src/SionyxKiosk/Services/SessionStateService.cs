using System.IO;
using System.Text.Json;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// Manages kiosk session state in a JSON file under C:\ProgramData\SIONYX\.
/// Survives power outages - on next boot, kiosk detects and cleans up stale sessions.
/// </summary>
public static class SessionStateService
{
    private static readonly ILogger Logger = Log.ForContext(typeof(SessionStateService));
    private static readonly string StateFile = @"C:\ProgramData\SIONYX\session.json";

    private static void WriteState(object state)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(StateFile)!);
            File.WriteAllText(StateFile, JsonSerializer.Serialize(state));
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] Failed to write state file"); }
    }

    private static Dictionary<string, object?> ReadState()
    {
        try
        {
            if (!File.Exists(StateFile)) return new();
            var json = File.ReadAllText(StateFile);
            return JsonSerializer.Deserialize<Dictionary<string, object?>>(json) ?? new();
        }
        catch { return new(); }
    }

    // -- Write --

    public static void SetSessionActive(string userId)
    {
        try
        {
            WriteState(new
            {
                ActiveSession  = 1,
                CurrentUser    = userId,
                SessionStart   = DateTime.UtcNow.ToString("o"),
                EnteredDesktop = 0
            });
            Logger.Information("[Session] Session started for user {UserId}", userId);
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] SetSessionActive failed"); }
    }

    public static void SetEnteredDesktop(bool entered)
    {
        try
        {
            var state = ReadState();
            state["EnteredDesktop"] = entered ? 1 : 0;
            WriteState(state);
            Logger.Information("[Session] EnteredDesktop = {Value}", entered);
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] SetEnteredDesktop failed"); }
    }

    public static void ClearSession()
    {
        try
        {
            WriteState(new
            {
                ActiveSession  = 0,
                CurrentUser    = "",
                EnteredDesktop = 0
            });
            Logger.Information("[Session] Session cleared");
        }
        catch (Exception ex) { Logger.Warning(ex, "[Session] ClearSession failed"); }
    }

    // -- Read --

    public static bool HasActiveSession()
    {
        var state = ReadState();
        return state.TryGetValue("ActiveSession", out var v) && v?.ToString() == "1";
    }

    public static bool HasEnteredDesktop()
    {
        var state = ReadState();
        return state.TryGetValue("EnteredDesktop", out var v) && v?.ToString() == "1";
    }

    public static string? GetCurrentUser()
    {
        var state = ReadState();
        return state.TryGetValue("CurrentUser", out var v) ? v?.ToString() : null;
    }
}