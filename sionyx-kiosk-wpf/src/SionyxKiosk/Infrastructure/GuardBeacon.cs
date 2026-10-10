using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Threading;
using Serilog;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Talks to the SionyxGuard Windows service (see docs/CRASH-GUARD.md):
///  - a dedicated thread writes a heartbeat every 2s, including the last time the UI thread
///    answered a ping, so the guard can tell "crashed", "UI frozen" and "whole process frozen" apart;
///  - MarkReady() says startup finished (guard lifts its lock screen);
///  - MarkCleanExit() says "I am closing on purpose" (admin exit, update, logoff) so the guard stays quiet.
/// The file format is parsed by SionyxGuard.Heartbeat - keep both in sync.
/// </summary>
public static class GuardBeacon
{
    private static readonly ILogger Logger = Log.ForContext(typeof(GuardBeacon));
    private static readonly string Dir = @"C:\ProgramData\SIONYX\guard";
    private static readonly string BeatFile = Path.Combine(Dir, "app.beat");
    private static readonly string CleanFile = Path.Combine(Dir, "app.clean");

    private static readonly object Gate = new();
    private static Thread? _thread;
    private static volatile bool _running;
    private static volatile bool _ready;
    private static bool _kiosk;
    private static long _uiTickMs = NowMs();
    private static int _pingPending;
    private static long _startMs;

    private static long NowMs() => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

    public static void Start(bool kiosk)
    {
        lock (Gate)
        {
            if (_thread != null) return;
            _kiosk = kiosk;
            _startMs = NowMs();
            _uiTickMs = _startMs;
            try
            {
                Directory.CreateDirectory(Dir);
                if (File.Exists(CleanFile)) File.Delete(CleanFile); // a previous clean exit no longer applies
            }
            catch (Exception ex) { Logger.Warning(ex, "[GuardBeacon] Could not prepare guard directory"); }

            _running = true;
            _thread = new Thread(Loop) { IsBackground = true, Name = "SionyxGuardBeacon" };
            _thread.Start();
        }
    }

    /// <summary>Startup finished and a window is on screen.</summary>
    public static void MarkReady() => _ready = true;

    /// <summary>Call from App.OnExit: every Shutdown() path in this app is intentional.</summary>
    public static void MarkCleanExit()
    {
        lock (Gate)
        {
            if (_thread == null) return;
            _running = false;
            try { File.WriteAllText(CleanFile, $"pid={Environment.ProcessId};ts={NowMs()}"); }
            catch (Exception ex) { Logger.Warning(ex, "[GuardBeacon] Could not write clean-exit marker"); }
        }
    }

    private static void Loop()
    {
        while (_running)
        {
            try
            {
                PingUi();
                var line = $"pid={Environment.ProcessId};start={_startMs};ts={NowMs()};ui={Interlocked.Read(ref _uiTickMs)};ready={(_ready ? 1 : 0)};kiosk={(_kiosk ? 1 : 0)}";
                var tmp = BeatFile + ".tmp";
                File.WriteAllText(tmp, line);
                File.Move(tmp, BeatFile, overwrite: true);
            }
            catch { /* best effort - the guard tolerates missing beats for a while */ }

            Thread.Sleep(2000);
        }
    }

    // Posts at most one outstanding ping. If the UI thread is blocked the callback never runs and
    // _uiTickMs goes stale, which is exactly the "frozen UI" signal the guard looks for.
    private static void PingUi()
    {
        var dispatcher = Application.Current?.Dispatcher;
        if (dispatcher == null || Interlocked.Exchange(ref _pingPending, 1) == 1) return;
        dispatcher.BeginInvoke(DispatcherPriority.Normal, new Action(() =>
        {
            Interlocked.Exchange(ref _uiTickMs, NowMs());
            Interlocked.Exchange(ref _pingPending, 0);
        }));
    }
}
