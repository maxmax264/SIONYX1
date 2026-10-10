namespace SionyxGuard;

// Pure decision logic for the crash guard. No Windows, I/O or clock access in
// here - everything arrives through the snapshot - so it is unit-tested on any OS
// (tests/SionyxGuard.Tests links this file directly).

/// <summary>Heartbeat the kiosk app writes every ~2s (see GuardBeacon in SionyxKiosk).</summary>
public sealed record Heartbeat(int Pid, DateTime StartedUtc, DateTime TimestampUtc, DateTime UiUtc, bool Ready, bool Kiosk)
{
    // Wire format (single line): pid=1;start=<unixMs>;ts=<unixMs>;ui=<unixMs>;ready=1;kiosk=1
    public static bool TryParse(string? text, out Heartbeat? beat)
    {
        beat = null;
        if (string.IsNullOrWhiteSpace(text)) return false;
        try
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var part in text.Trim().Split(';', StringSplitOptions.RemoveEmptyEntries))
            {
                var i = part.IndexOf('=');
                if (i > 0) map[part[..i].Trim()] = part[(i + 1)..].Trim();
            }
            if (!map.TryGetValue("pid", out var pid) || !int.TryParse(pid, out var pidVal)) return false;
            if (!TryMs(map, "start", out var start) || !TryMs(map, "ts", out var ts) || !TryMs(map, "ui", out var ui)) return false;
            beat = new Heartbeat(pidVal, start, ts, ui,
                map.TryGetValue("ready", out var r) && r == "1",
                !map.TryGetValue("kiosk", out var k) || k == "1");
            return true;
        }
        catch { return false; }
    }

    public string Serialize() =>
        $"pid={Pid};start={Ms(StartedUtc)};ts={Ms(TimestampUtc)};ui={Ms(UiUtc)};ready={(Ready ? 1 : 0)};kiosk={(Kiosk ? 1 : 0)}";

    private static long Ms(DateTime utc) => new DateTimeOffset(DateTime.SpecifyKind(utc, DateTimeKind.Utc)).ToUnixTimeMilliseconds();

    private static bool TryMs(Dictionary<string, string> map, string key, out DateTime value)
    {
        value = default;
        if (!map.TryGetValue(key, out var s) || !long.TryParse(s, out var ms)) return false;
        value = DateTimeOffset.FromUnixTimeMilliseconds(ms).UtcDateTime;
        return true;
    }
}

public enum AppHealth
{
    /// <summary>Guard disabled (kill switch) or app running without --kiosk: nothing to do.</summary>
    Unsupervised,
    /// <summary>Nobody is logged on - nothing to protect.</summary>
    NoSession,
    /// <summary>An installer is running; the app is being replaced on purpose.</summary>
    Maintenance,
    /// <summary>App is alive, responsive and finished starting.</summary>
    Healthy,
    /// <summary>App is starting (or the logon task hasn't launched it yet) - give it time.</summary>
    Starting,
    /// <summary>App exited through its own shutdown path (admin exit, update, logoff).</summary>
    CleanExit,
    /// <summary>App process is gone without a clean exit.</summary>
    Crashed,
    /// <summary>App process is alive but frozen (UI thread or whole process).</summary>
    Hung,
    /// <summary>User logged on but the app never started.</summary>
    NeverStarted,
}

public sealed record GuardSettings
{
    /// <summary>UI thread / heartbeat thread silent for this long = hung.</summary>
    public TimeSpan HangTimeout { get; init; } = TimeSpan.FromSeconds(15);
    /// <summary>A starting app must reach "ready" within this long.</summary>
    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(60);
    /// <summary>After logon, the app must exist within this long (logon task + .NET startup).</summary>
    public TimeSpan NeverStartedTimeout { get; init; } = TimeSpan.FromSeconds(90);
    /// <summary>After a guard-launched app, wait this long for "ready" before trying again.</summary>
    public TimeSpan ReadyTimeout { get; init; } = TimeSpan.FromSeconds(20);
    /// <summary>App launches per incident before escalating to a forced logoff.</summary>
    public int MaxLaunchAttempts { get; init; } = 2;
    /// <summary>More than this many forced logoffs inside LogoffWindow = fail closed (stay locked).</summary>
    public int MaxLogoffsInWindow { get; init; } = 3;
    public TimeSpan LogoffWindow { get; init; } = TimeSpan.FromMinutes(15);
}

public sealed record GuardSnapshot(
    DateTime NowUtc,
    bool Disabled,
    bool SessionActive,
    DateTime SessionStartedUtc,
    bool MaintenanceActive,
    bool AppRunning,
    int AppPid,
    DateTime AppFirstSeenUtc,
    bool AppEverSeenThisSession,
    Heartbeat? Beat,
    DateTime? CleanExitUtc);

public enum RecoveryStep { LaunchApp, Wait, LogOff, FailClosed }

public sealed class Incident
{
    public DateTime StartedUtc { get; init; }
    public AppHealth Reason { get; init; }
    public int Launches { get; set; }
    public DateTime? LastLaunchUtc { get; set; }
    public bool LoggedOff { get; set; }
}

public static class GuardPolicy
{
    public static AppHealth Classify(GuardSnapshot s, GuardSettings cfg)
    {
        if (s.Disabled) return AppHealth.Unsupervised;
        if (!s.SessionActive) return AppHealth.NoSession;
        if (s.MaintenanceActive) return AppHealth.Maintenance;

        if (s.AppRunning)
        {
            var beat = s.Beat is { } b && b.Pid == s.AppPid ? b : null;
            if (beat is { Kiosk: false }) return AppHealth.Unsupervised;

            if (beat == null)
                return s.NowUtc - s.AppFirstSeenUtc > cfg.StartupTimeout ? AppHealth.Hung : AppHealth.Starting;

            if (!beat.Ready)
                return s.NowUtc - beat.StartedUtc > cfg.StartupTimeout ? AppHealth.Hung : AppHealth.Starting;

            if (s.NowUtc - beat.UiUtc > cfg.HangTimeout || s.NowUtc - beat.TimestampUtc > cfg.HangTimeout)
                return AppHealth.Hung;
            return AppHealth.Healthy;
        }

        // App process is gone.
        if (s.CleanExitUtc is { } exit && exit >= s.SessionStartedUtc) return AppHealth.CleanExit;
        if (s.AppEverSeenThisSession) return AppHealth.Crashed;
        return s.NowUtc - s.SessionStartedUtc > cfg.NeverStartedTimeout ? AppHealth.NeverStarted : AppHealth.Starting;
    }

    public static bool IsFault(AppHealth h) => h is AppHealth.Crashed or AppHealth.Hung or AppHealth.NeverStarted;

    public static RecoveryStep Escalate(Incident incident, IReadOnlyCollection<DateTime> recentLogoffsUtc, DateTime nowUtc, GuardSettings cfg)
    {
        var logoffsInWindow = recentLogoffsUtc.Count(t => nowUtc - t <= cfg.LogoffWindow);
        if (incident.LoggedOff)
            return logoffsInWindow > cfg.MaxLogoffsInWindow ? RecoveryStep.FailClosed : RecoveryStep.Wait;

        if (incident.Launches == 0 || incident.LastLaunchUtc is null)
            return logoffsInWindow >= cfg.MaxLogoffsInWindow ? RecoveryStep.FailClosed : RecoveryStep.LaunchApp;

        if (nowUtc - incident.LastLaunchUtc.Value < cfg.ReadyTimeout) return RecoveryStep.Wait;

        if (incident.Launches < cfg.MaxLaunchAttempts) return RecoveryStep.LaunchApp;
        return logoffsInWindow >= cfg.MaxLogoffsInWindow ? RecoveryStep.FailClosed : RecoveryStep.LogOff;
    }
}
