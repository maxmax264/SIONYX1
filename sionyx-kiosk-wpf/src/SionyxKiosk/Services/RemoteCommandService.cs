using System.Diagnostics;
using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

/// <summary>
/// Listens for dashboard-issued power commands (shutdown / restart) on
/// "computers/{id}/powerCommand/requested", same SseListener pattern as
/// VncRelayService and LogShippingControlService. Runs the
/// Windows `shutdown.exe` utility, reports the outcome to
/// "computers/{id}/powerCommand/lastResult", then clears "requested" so
/// the same command isn't re-applied on the next SSE reconnect (Firebase
/// replays existing data as an initial "put" when a listener (re)starts).
///
/// Uses its OWN anonymous Firebase identity (like ComputerHeartbeatService
/// and VncRelayService), not the shared app-wide FirebaseClient. That
/// shared client only ever holds a token while an actual customer is
/// logged in on the kiosk - this listener needs to work at any time
/// (including the idle login screen), so it can't depend on that. Bug
/// found in the field: this used to take the shared FirebaseClient, so a
/// restart/shutdown issued from the dashboard while the kiosk was idle was
/// silently dropped - it only actually executed once a customer happened
/// to log in afterwards (at which point Firebase replayed the still-
/// pending "requested" node the moment the listener could finally
/// connect), making it look like the reboot came out of nowhere right
/// after login.
/// </summary>
public class RemoteCommandService
{
    private static readonly ILogger Logger = Log.ForContext<RemoteCommandService>();
    private const int SignInRetrySeconds = 30;

    private readonly FirebaseClient _firebase;
    private string? _computerId;
    // Polled, not streamed: a power command does not need sub-second delivery,
    // and a permanent SSE connection per kiosk counts against Firebase's
    // simultaneous-connection cap. See DbPoller.
    private DbPoller? _listener;
    internal static readonly TimeSpan PollInterval = TimeSpan.FromSeconds(30);
    private bool _starting;
    private bool _signedIn;

    // Guards against acting twice on the same command - e.g. the SSE
    // stream reconnecting and Firebase replaying the still-present
    // "requested" node as a fresh "put" event before our own delete of it
    // round-trips.
    private long _lastHandledRequestedAt;

    // A command older than this is never executed. Firebase replays the
    // still-present "requested" node as an initial "put" on EVERY listener
    // (re)start - including the first one after the very reboot this
    // command caused. If the delete of the node didn't make it out before
    // Windows went down (the kiosk network is flaky/filtered, and the old
    // code deleted only AFTER launching shutdown.exe /t 5), the node was
    // still there on boot, the in-memory _lastHandledRequestedAt was gone,
    // and the kiosk would restart itself again - a reboot loop.
    internal static readonly TimeSpan MaxCommandAge = TimeSpan.FromMinutes(10);
    internal const string LastHandledRegistryValue = "LastPowerCommandRequestedAt";

    // Seams (defaults = production behaviour; unit tests replace them so
    // a test can NEVER really call shutdown.exe or touch the registry).
    internal Func<long> NowMs { get; set; } = () => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
    internal Func<long> LoadLastHandled { get; set; } = () =>
        long.TryParse(RegistryConfig.ReadValueCurrentUser(LastHandledRegistryValue), out var v) ? v : 0;
    internal Action<long> SaveLastHandled { get; set; } = v =>
        RegistryConfig.WriteValue(LastHandledRegistryValue, v.ToString());
    internal Action<string> RunPowerAction { get; set; } = DefaultRunPowerAction;

    /// <summary>True when the command was issued too long ago (or is dated
    /// implausibly far in the future - a badly wrong clock) to be safe to
    /// execute now.</summary>
    internal static bool IsStale(long requestedAtMs, long nowMs, TimeSpan maxAge)
    {
        var limit = (long)maxAge.TotalMilliseconds;
        var ageMs = nowMs - requestedAtMs;
        return ageMs > limit || ageMs < -limit;
    }

    public RemoteCommandService(FirebaseConfig config)
    {
        _firebase = new FirebaseClient(config);
    }

    /// <summary>Call once at startup - does not need the kiosk to be
    /// authenticated (see class remarks: this keeps its own anonymous
    /// identity so it works at the idle login screen too).</summary>
    public void Start()
    {
        if (_starting || _signedIn) return;
        _computerId = DeviceInfo.GetDeviceId();

        _ = Task.Run(async () =>
        {
            _starting = true;
            try { await EnsureSignedInAndListeningAsync(); }
            finally { _starting = false; }
        });
    }

    private async Task EnsureSignedInAndListeningAsync()
    {
        var signIn = await _firebase.SignInAnonymouslyAsync();
        if (!signIn.Success)
        {
            Logger.Warning("RemoteCommand anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, (int)(FirebaseClient.SignInRetryMs(SignInRetrySeconds) / 1000));
            var retryTimer = new System.Timers.Timer(FirebaseClient.SignInRetryMs(SignInRetrySeconds)) { AutoReset = false };
            retryTimer.Elapsed += async (_, _) =>
            {
                retryTimer.Dispose();
                await EnsureSignedInAndListeningAsync();
            };
            retryTimer.Start();
            return;
        }

        _signedIn = true;
        _listener?.Stop();
        _listener = _firebase.DbPoll(
            $"computers/{_computerId}/powerCommand/requested",
            PollInterval,
            value => OnCommandRequested("put", value));
    }

    internal void OnCommandRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        if (data == null || data.Value.ValueKind != JsonValueKind.Object) return;

        var obj = data.Value;
        var type = obj.TryGetProperty("type", out var t) && t.ValueKind == JsonValueKind.String ? t.GetString() : null;
        var requestedAt = obj.TryGetProperty("requestedAt", out var r) && r.TryGetInt64(out var ra) ? ra : 0;

        if (string.IsNullOrEmpty(type) || requestedAt == 0) return;

        // Already handled: in this process (SSE replay) OR by a previous
        // process (the persisted value survives the reboot the command
        // itself caused). EQUALITY on purpose, not "older than": the only
        // node that can still be sitting there is the last one we handled,
        // and admins' PCs can have skewed clocks, so a genuinely new
        // command may carry a smaller timestamp than the previous one.
        if (requestedAt == _lastHandledRequestedAt || requestedAt == LoadLastHandled()) return;

        // Remember it BEFORE doing anything else, so no later failure (or a
        // crash/reboot in the middle) can ever make us run it a second time.
        _lastHandledRequestedAt = requestedAt;
        SaveLastHandled(requestedAt);

        if (IsStale(requestedAt, NowMs(), MaxCommandAge))
        {
            Logger.Warning("Ignoring stale power command '{Type}' (requestedAt={RequestedAt}) - older than {Minutes} min; clearing it", type, requestedAt, MaxCommandAge.TotalMinutes);
            _ = Task.Run(ClearRequestedAsync);
            return;
        }

        if (type != "shutdown" && type != "restart")
        {
            Logger.Warning("Unknown power command type '{Type}' - ignoring", type);
            return;
        }

        Logger.Warning("Power command received from dashboard: {Type}", type);
        _ = Task.Run(() => ExecuteAsync(type));
    }

    internal async Task ExecuteAsync(string type)
    {
        try
        {
            await ReportResultAsync(type, "executing");

            // Clear the request FIRST. The old order (shutdown.exe first,
            // delete after) only left the 5-second /t window for the delete
            // to reach Firebase; on this network that often isn't enough.
            // Even if this delete fails now, the persisted last-handled
            // value and the max-age check above keep it from replaying.
            await ClearRequestedAsync();

            // /t 5 gives a few seconds for any in-flight Firebase calls
            // (heartbeat, etc.) to flush before Windows tears the process down.
            RunPowerAction(type);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to execute power command '{Type}'", type);
            await ReportResultAsync(type, "failed: " + ex.Message);
        }
    }

    private static void DefaultRunPowerAction(string type)
    {
        var args = type == "shutdown" ? "/s /t 5" : "/r /t 5";
        var psi = new ProcessStartInfo
        {
            FileName = "shutdown.exe",
            Arguments = args,
            UseShellExecute = true,
            CreateNoWindow = true,
            WindowStyle = ProcessWindowStyle.Hidden,
        };
        Process.Start(psi);

        Logger.Warning("shutdown.exe invoked ({Args}) - machine will {Type} in 5s", args, type);
    }

    private async Task ReportResultAsync(string type, string status)
    {
        try
        {
            await _firebase.DbUpdateAsync($"computers/{_computerId}/powerCommand",
                new Dictionary<string, object>
                {
                    ["lastResult"] = new
                    {
                        type,
                        status,
                        at = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                    },
                });
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to report power-command result (non-fatal)");
        }
    }

    /// <summary>Clears "requested" so a later SSE reconnect doesn't replay
    /// and re-execute the same command.</summary>
    private async Task ClearRequestedAsync()
    {
        try
        {
            // DbDeleteAsync reports failure through its result, it does not
            // throw - so the result has to be looked at, otherwise a failed
            // delete is completely invisible.
            var result = await _firebase.DbDeleteAsync($"computers/{_computerId}/powerCommand/requested");
            if (!result.Success)
                Logger.Warning("Failed to clear powerCommand/requested: {Error} (non-fatal - replay is blocked by the persisted last-handled value)", result.Error);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to clear powerCommand/requested (non-fatal)");
        }
    }

    public void Stop()
    {
        _listener?.Stop();
    }
}
