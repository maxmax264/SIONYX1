using SionyxGuard;

namespace SionyxGuard.Tests;

public class GuardPolicyTests
{
    private static readonly DateTime T0 = new(2026, 10, 11, 12, 0, 0, DateTimeKind.Utc);
    private static readonly GuardSettings Cfg = new();

    private static Heartbeat Beat(DateTime now, int pid = 100, bool ready = true, bool kiosk = true, double uiAgeSec = 1, double tsAgeSec = 1, double startedAgoSec = 600)
        => new(pid, now.AddSeconds(-startedAgoSec), now.AddSeconds(-tsAgeSec), now.AddSeconds(-uiAgeSec), ready, kiosk);

    private static GuardSnapshot Snap(DateTime now, bool running = true, int pid = 100, Heartbeat? beat = null,
        bool everSeen = true, DateTime? cleanExit = null, bool disabled = false, bool session = true,
        bool maintenance = false, double sessionAgeSec = 3600, double pidSeenAgoSec = 600)
        => new(now, disabled, session, now.AddSeconds(-sessionAgeSec), maintenance, running, running ? pid : 0,
               now.AddSeconds(-pidSeenAgoSec), everSeen, beat, cleanExit);

    // ---- Heartbeat wire format ----

    [Fact]
    public void Heartbeat_RoundTrips()
    {
        var b = new Heartbeat(4242, T0.AddMinutes(-5), T0, T0.AddSeconds(-1), true, true);
        Assert.True(Heartbeat.TryParse(b.Serialize(), out var parsed));
        Assert.Equal(b, parsed);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("garbage")]
    [InlineData("pid=abc;start=1;ts=1;ui=1")]
    [InlineData("pid=1;start=1;ts=1")] // missing ui
    public void Heartbeat_RejectsBadInput(string? text)
    {
        Assert.False(Heartbeat.TryParse(text, out var beat));
        Assert.Null(beat);
    }

    // ---- Classification ----

    [Fact]
    public void Disabled_IsUnsupervised() =>
        Assert.Equal(AppHealth.Unsupervised, GuardPolicy.Classify(Snap(T0, running: false, disabled: true), Cfg));

    [Fact]
    public void NoSession_IsNoSession() =>
        Assert.Equal(AppHealth.NoSession, GuardPolicy.Classify(Snap(T0, running: false, session: false), Cfg));

    [Fact]
    public void InstallerRunning_IsMaintenance_EvenIfAppIsGone() =>
        Assert.Equal(AppHealth.Maintenance, GuardPolicy.Classify(Snap(T0, running: false, maintenance: true), Cfg));

    [Fact]
    public void FreshReadyBeat_IsHealthy() =>
        Assert.Equal(AppHealth.Healthy, GuardPolicy.Classify(Snap(T0, beat: Beat(T0)), Cfg));

    [Fact]
    public void NonKioskRun_IsUnsupervised() =>
        Assert.Equal(AppHealth.Unsupervised, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, kiosk: false, uiAgeSec: 999)), Cfg));

    [Fact]
    public void FrozenUiThread_IsHung() =>
        Assert.Equal(AppHealth.Hung, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, uiAgeSec: 30)), Cfg));

    [Fact]
    public void FrozenWholeProcess_IsHung() =>
        Assert.Equal(AppHealth.Hung, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, uiAgeSec: 30, tsAgeSec: 30)), Cfg));

    [Fact]
    public void ShortUiStall_IsStillHealthy() =>
        Assert.Equal(AppHealth.Healthy, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, uiAgeSec: 8)), Cfg));

    [Fact]
    public void StaleBeatFromPreviousPid_IsIgnored_AppStillStarting() =>
        Assert.Equal(AppHealth.Starting, GuardPolicy.Classify(Snap(T0, pid: 200, beat: Beat(T0, pid: 100), pidSeenAgoSec: 5), Cfg));

    [Fact]
    public void NoBeatForTooLong_IsHung() =>
        Assert.Equal(AppHealth.Hung, GuardPolicy.Classify(Snap(T0, pid: 200, beat: null, pidSeenAgoSec: 120), Cfg));

    [Fact]
    public void NotReadyWithinStartupTimeout_IsStarting() =>
        Assert.Equal(AppHealth.Starting, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, ready: false, startedAgoSec: 20)), Cfg));

    [Fact]
    public void NotReadyBeyondStartupTimeout_IsHung() =>
        Assert.Equal(AppHealth.Hung, GuardPolicy.Classify(Snap(T0, beat: Beat(T0, ready: false, startedAgoSec: 120)), Cfg));

    [Fact]
    public void ProcessGoneWithoutMarker_IsCrashed() =>
        Assert.Equal(AppHealth.Crashed, GuardPolicy.Classify(Snap(T0, running: false, everSeen: true), Cfg));

    [Fact]
    public void ProcessGoneWithFreshCleanExitMarker_IsCleanExit() =>
        Assert.Equal(AppHealth.CleanExit, GuardPolicy.Classify(Snap(T0, running: false, cleanExit: T0.AddSeconds(-2)), Cfg));

    [Fact]
    public void CleanExitMarkerFromEarlierSession_DoesNotMaskCrash() =>
        Assert.Equal(AppHealth.Crashed, GuardPolicy.Classify(Snap(T0, running: false, cleanExit: T0.AddDays(-1), sessionAgeSec: 600), Cfg));

    [Fact]
    public void LoggedOnButAppNeverStartedWithinGrace_IsStarting() =>
        Assert.Equal(AppHealth.Starting, GuardPolicy.Classify(Snap(T0, running: false, everSeen: false, sessionAgeSec: 30), Cfg));

    [Fact]
    public void LoggedOnButAppNeverStartedAfterGrace_IsNeverStarted() =>
        Assert.Equal(AppHealth.NeverStarted, GuardPolicy.Classify(Snap(T0, running: false, everSeen: false, sessionAgeSec: 120), Cfg));

    [Theory]
    [InlineData(AppHealth.Crashed, true)]
    [InlineData(AppHealth.Hung, true)]
    [InlineData(AppHealth.NeverStarted, true)]
    [InlineData(AppHealth.Healthy, false)]
    [InlineData(AppHealth.Starting, false)]
    [InlineData(AppHealth.CleanExit, false)]
    [InlineData(AppHealth.Maintenance, false)]
    public void IsFault_OnlyForRealFailures(AppHealth health, bool expected) =>
        Assert.Equal(expected, GuardPolicy.IsFault(health));

    // ---- Escalation ----

    private static readonly List<DateTime> NoLogoffs = new();

    [Fact]
    public void FreshIncident_LaunchesImmediately() =>
        Assert.Equal(RecoveryStep.LaunchApp, GuardPolicy.Escalate(new Incident { StartedUtc = T0 }, NoLogoffs, T0, Cfg));

    [Fact]
    public void AfterLaunch_WaitsForReady()
    {
        var inc = new Incident { StartedUtc = T0, Launches = 1, LastLaunchUtc = T0 };
        Assert.Equal(RecoveryStep.Wait, GuardPolicy.Escalate(inc, NoLogoffs, T0.AddSeconds(10), Cfg));
    }

    [Fact]
    public void ReadyTimeout_RetriesLaunch_ThenLogsOff()
    {
        var inc = new Incident { StartedUtc = T0, Launches = 1, LastLaunchUtc = T0 };
        Assert.Equal(RecoveryStep.LaunchApp, GuardPolicy.Escalate(inc, NoLogoffs, T0.AddSeconds(25), Cfg));

        inc = new Incident { StartedUtc = T0, Launches = 2, LastLaunchUtc = T0 };
        Assert.Equal(RecoveryStep.LogOff, GuardPolicy.Escalate(inc, NoLogoffs, T0.AddSeconds(25), Cfg));
    }

    [Fact]
    public void AfterLogoff_WaitsForSessionToEnd()
    {
        var inc = new Incident { StartedUtc = T0, Launches = 2, LastLaunchUtc = T0, LoggedOff = true };
        Assert.Equal(RecoveryStep.Wait, GuardPolicy.Escalate(inc, new[] { T0 }, T0.AddSeconds(5), Cfg));
    }

    [Fact]
    public void TooManyRecentLogoffs_FailsClosed()
    {
        var logoffs = new[] { T0.AddMinutes(-9), T0.AddMinutes(-6), T0.AddMinutes(-3) };
        var inc = new Incident { StartedUtc = T0 };
        Assert.Equal(RecoveryStep.FailClosed, GuardPolicy.Escalate(inc, logoffs, T0, Cfg));

        inc = new Incident { StartedUtc = T0, Launches = 2, LastLaunchUtc = T0.AddSeconds(-30) };
        Assert.Equal(RecoveryStep.FailClosed, GuardPolicy.Escalate(inc, logoffs, T0, Cfg));
    }

    [Fact]
    public void OldLogoffs_DoNotCountTowardsTheLimit()
    {
        var logoffs = new[] { T0.AddHours(-3), T0.AddHours(-2), T0.AddHours(-1) };
        Assert.Equal(RecoveryStep.LaunchApp, GuardPolicy.Escalate(new Incident { StartedUtc = T0 }, logoffs, T0, Cfg));
    }
}
