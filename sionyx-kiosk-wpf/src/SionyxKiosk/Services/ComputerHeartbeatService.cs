using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

public class ComputerHeartbeatService
{
    private static readonly ILogger Logger = Log.ForContext<ComputerHeartbeatService>();
    private const int IntervalSeconds = 60;
    private const int SignInRetrySeconds = 30;

    private readonly FirebaseClient _deviceFirebase;
    private readonly string _computerId;
    private System.Timers.Timer? _timer;
    private bool _starting;
    private bool _signedIn;

    public ComputerHeartbeatService(FirebaseConfig config)
    {
        _deviceFirebase = new FirebaseClient(config);
        _computerId = DeviceInfo.GetDeviceId();
    }

    /// <summary>
    /// Starts reporting "alive" heartbeats to the dashboard, independent of any
    /// logged-in user (called once from the auth/login screen at app startup).
    ///
    /// Bug fixed: this used to give up permanently if the one-off anonymous
    /// Firebase sign-in failed on its very first attempt - e.g. a transient
    /// network hiccup right at boot, or a NetFree-style filter that hasn't
    /// finished warming up yet. Since Start() is only called once (from
    /// StartGlobalHotkey, guarded so it can't run twice), that single failure
    /// meant NO heartbeat for the rest of the session - which looked exactly
    /// like "no signal until a user logs in", because by the time a user logs
    /// in the network/filter has usually settled and other Firebase calls
    /// (that DO retry per-call) start working. Now sign-in retries on a timer
    /// until it succeeds, instead of failing silently once and never trying again.
    /// </summary>
    public void Start()
    {
        if (_timer != null || _starting || _signedIn) return;

        _ = Task.Run(async () =>
        {
            _starting = true;
            try
            {
                await EnsureSignedInAndReportingAsync();
            }
            finally
            {
                _starting = false;
            }
        });
    }

    private async Task EnsureSignedInAndReportingAsync()
    {
        var signIn = await _deviceFirebase.SignInAnonymouslyAsync();
        if (!signIn.Success)
        {
            Logger.Warning("Heartbeat anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, SignInRetrySeconds);
            var retryTimer = new System.Timers.Timer(SignInRetrySeconds * 1000) { AutoReset = false };
            retryTimer.Elapsed += async (_, _) =>
            {
                retryTimer.Dispose();
                await EnsureSignedInAndReportingAsync();
            };
            retryTimer.Start();
            return;
        }

        _signedIn = true;
        await SendHeartbeatAsync();

        _timer = new System.Timers.Timer(IntervalSeconds * 1000);
        _timer.Elapsed += async (_, _) => await SendHeartbeatAsync();
        _timer.AutoReset = true;
        _timer.Start();
    }

    private async Task SendHeartbeatAsync()
    {
        try
        {
            var result = await _deviceFirebase.DbUpdateAsync($"computers/{_computerId}",
                new Dictionary<string, object>
                {
                    ["heartbeatAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                });
            if (!result.Success)
                Logger.Warning("Heartbeat write failed: {Error}", result.Error);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Heartbeat write threw (non-fatal)");
        }
    }

    public void Stop()
    {
        _timer?.Stop();
        _timer?.Dispose();
        _timer = null;
        _signedIn = false;
    }
}