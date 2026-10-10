using System.Diagnostics;
using System.Runtime.InteropServices;
using Microsoft.Win32;
using Serilog;

namespace SionyxGuard;

/// <summary>
/// Supervision loop (1s tick). Detects crash / hang / never-started of SionyxKiosk.exe in the
/// console session, covers the screen at once, relaunches the app, and escalates to a forced
/// logoff (AutoAdminLogon + logon task then restart everything clean) if recovery fails.
/// All decisions live in GuardPolicy; this class only gathers facts and performs actions.
/// </summary>
internal sealed class GuardWorker : BackgroundService
{
    private static readonly ILogger Logger = Log.ForContext<GuardWorker>();
    private static readonly string[] BlockedWhileLocked = { "taskmgr", "cmd", "powershell", "pwsh", "regedit", "mmc" };

    private readonly GuardSettings _cfg = new();
    private readonly List<DateTime> _logoffs = new();

    private uint _session = Native.InvalidSession;
    private DateTime _sessionStarted;
    private bool _appEverSeen;
    private int _trackedPid;
    private DateTime _pidFirstSeen;
    private Heartbeat? _lastBeat;
    private Incident? _incident;
    private bool _failClosedLogged;
    private DateTime _lastLockLaunch = DateTime.MinValue;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        Logger.Information("SionyxGuard started");
        Directory.CreateDirectory(GuardPaths.Dir);

        while (!stoppingToken.IsCancellationRequested)
        {
            try { Tick(); }
            catch (Exception ex) { Logger.Error(ex, "Guard tick failed"); }

            try { await Task.Delay(1000, stoppingToken); }
            catch (OperationCanceledException) { break; }
        }
    }

    public override Task StopAsync(CancellationToken cancellationToken)
    {
        // Service stopping on purpose (upgrade/uninstall/shutdown): never leave a lock behind.
        ReleaseLock();
        Logger.Information("SionyxGuard stopped");
        return base.StopAsync(cancellationToken);
    }

    private void Tick()
    {
        var now = DateTime.UtcNow;
        var disabled = IsDisabled();
        var (sid, hasUser) = GetConsoleSession();

        if (sid == Native.InvalidSession || !hasUser)
        {
            ResetSession();
            ReleaseLock();
            return;
        }

        if (sid != _session)
        {
            ResetSession();
            _session = sid;
            _sessionStarted = now;
            Logger.Information("Tracking session {Session}", sid);
        }

        var app = FindApp(sid);
        if (app != null)
        {
            _appEverSeen = true;
            if (app.Id != _trackedPid) { _trackedPid = app.Id; _pidFirstSeen = now; }
        }

        if (TryReadBeat(out var beat)) _lastBeat = beat;

        var snap = new GuardSnapshot(
            now, disabled, true, _sessionStarted, InstallerRunning(),
            app != null, app?.Id ?? 0, _pidFirstSeen, _appEverSeen, _lastBeat, ReadCleanExit());

        var health = GuardPolicy.Classify(snap, _cfg);

        if (_incident == null)
        {
            if (!GuardPolicy.IsFault(health)) return;
            _incident = new Incident { StartedUtc = now, Reason = health };
            _failClosedLogged = false;
            Logger.Warning("INCIDENT opened: {Reason} (session {Session}) - locking screen", health, sid);
        }
        else if (health == AppHealth.Healthy && _incident.Launches > 0)
        {
            Logger.Information("INCIDENT resolved after {Seconds:F0}s ({Launches} launches) - unlocking", (now - _incident.StartedUtc).TotalSeconds, _incident.Launches);
            _incident = null;
            ReleaseLock();
            return;
        }
        else if (health is AppHealth.Healthy or AppHealth.CleanExit or AppHealth.Maintenance or AppHealth.Unsupervised)
        {
            // Came back on its own (e.g. the logon task finally launched it) or was stopped on purpose.
            Logger.Information("INCIDENT cleared: health is now {Health}", health);
            _incident = null;
            ReleaseLock();
            return;
        }

        EnsureLock(sid);
        KillBlockedTools(sid);

        switch (GuardPolicy.Escalate(_incident, _logoffs, now, _cfg))
        {
            case RecoveryStep.LaunchApp:
                RelaunchApp(sid, app, now);
                break;
            case RecoveryStep.LogOff:
                Logger.Error("Recovery failed after {Launches} launches - forcing logoff of session {Session}", _incident.Launches, sid);
                _logoffs.Add(now);
                _incident.LoggedOff = true;
                if (!Native.WTSLogoffSession(IntPtr.Zero, sid, false))
                    Logger.Error("WTSLogoffSession failed: {Err}", Marshal.GetLastWin32Error());
                break;
            case RecoveryStep.FailClosed:
                if (!_failClosedLogged)
                {
                    Logger.Error("Too many failed recoveries - staying locked until an administrator intervenes");
                    _failClosedLogged = true;
                }
                break;
            case RecoveryStep.Wait:
                break;
        }
    }

    private void RelaunchApp(uint sid, Process? existing, DateTime now)
    {
        if (existing != null)
        {
            Logger.Warning("Killing hung SionyxKiosk (pid {Pid})", existing.Id);
            try { existing.Kill(entireProcessTree: true); existing.WaitForExit(5000); } catch (Exception ex) { Logger.Warning(ex, "Kill failed"); }
        }

        var exe = ResolveAppPath();
        _incident!.Launches++;
        _incident.LastLaunchUtc = now;
        _appEverSeen = true;
        var pid = SessionLauncher.Launch(sid, exe, "--kiosk");
        Logger.Information("Relaunch #{N} of {Exe}: pid={Pid}", _incident.Launches, exe, pid);
    }

    // ---------------------------------------------------------------- facts

    private static bool IsDisabled()
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(GuardPaths.DisableKey);
            return key?.GetValue(GuardPaths.DisableValue) is int v && v == 1;
        }
        catch { return false; }
    }

    private static (uint Session, bool HasUser) GetConsoleSession()
    {
        var sid = Native.WTSGetActiveConsoleSessionId();
        if (sid == Native.InvalidSession) return (sid, false);

        IntPtr buf = IntPtr.Zero;
        try
        {
            if (!Native.WTSQuerySessionInformation(IntPtr.Zero, sid, Native.WTSUserName, out buf, out _)) return (sid, false);
            var user = Marshal.PtrToStringUni(buf);
            return (sid, !string.IsNullOrEmpty(user));
        }
        finally { if (buf != IntPtr.Zero) Native.WTSFreeMemory(buf); }
    }

    private static Process? FindApp(uint sid)
    {
        foreach (var p in Process.GetProcessesByName("SionyxKiosk"))
        {
            try { if ((uint)p.SessionId == sid) return p; } catch { }
        }
        return null;
    }

    private static bool InstallerRunning()
    {
        // Windows Installer holds this mutex for the whole duration of an install/upgrade.
        try { using var m = Mutex.OpenExisting(@"Global\_MSIExecute"); return true; }
        catch (WaitHandleCannotBeOpenedException) { return false; }
        catch { return false; }
    }

    private static bool TryReadBeat(out Heartbeat? beat)
    {
        beat = null;
        try
        {
            if (!File.Exists(GuardPaths.Beat)) return false;
            using var fs = new FileStream(GuardPaths.Beat, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            using var sr = new StreamReader(fs);
            return Heartbeat.TryParse(sr.ReadToEnd(), out beat);
        }
        catch { return false; }
    }

    private static DateTime? ReadCleanExit()
    {
        try { return File.Exists(GuardPaths.CleanExit) ? File.GetLastWriteTimeUtc(GuardPaths.CleanExit) : null; }
        catch { return null; }
    }

    private static string ResolveAppPath()
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(GuardPaths.DisableKey);
            if (key?.GetValue("AppPath") is string p && File.Exists(p)) return p;
        }
        catch { }
        // Layout: <INSTALLFOLDER>\Guard\SionyxGuard.exe next to <INSTALLFOLDER>\SionyxKiosk.exe
        return Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "SionyxKiosk.exe"));
    }

    private void ResetSession()
    {
        _session = Native.InvalidSession;
        _appEverSeen = false;
        _trackedPid = 0;
        _lastBeat = null;
        _incident = null;
    }

    // ---------------------------------------------------------------- lock

    private void EnsureLock(uint sid)
    {
        try { File.WriteAllText(GuardPaths.LockFlag, DateTime.UtcNow.ToString("o")); }
        catch (Exception ex) { Logger.Warning(ex, "Could not refresh lock flag"); }

        if (LockRunning(sid) || DateTime.UtcNow - _lastLockLaunch < TimeSpan.FromSeconds(2)) return;
        _lastLockLaunch = DateTime.UtcNow;
        var exe = Environment.ProcessPath ?? Path.Combine(AppContext.BaseDirectory, "SionyxGuard.exe");
        var pid = SessionLauncher.Launch(sid, exe, "--lock");
        Logger.Information("Lock screen launched: pid={Pid}", pid);
    }

    private static bool LockRunning(uint sid)
    {
        foreach (var p in Process.GetProcessesByName("SionyxGuard"))
        {
            try { if ((uint)p.SessionId == sid) return true; } catch { }
        }
        return false;
    }

    private void ReleaseLock()
    {
        try { if (File.Exists(GuardPaths.LockFlag)) File.Delete(GuardPaths.LockFlag); } catch { }
        // The lock exits on its own when the flag disappears; this is just a safety net.
        foreach (var p in Process.GetProcessesByName("SionyxGuard"))
        {
            try { if (p.SessionId != 0 && p.Id != Environment.ProcessId) { p.WaitForExit(1500); if (!p.HasExited) p.Kill(); } } catch { }
        }
    }

    private static void KillBlockedTools(uint sid)
    {
        foreach (var name in BlockedWhileLocked)
        {
            foreach (var p in Process.GetProcessesByName(name))
            {
                try { if ((uint)p.SessionId == sid) p.Kill(); } catch { }
            }
        }
    }
}
