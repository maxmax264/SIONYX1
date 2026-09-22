using System.Net.Http;
using System.Text.Json;
using Serilog;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Watches whether the org's local PC (running Understood / sionyx-vnc-relay /
/// sionyx-auth-server as Windows services, see the SIONYX failover plan doc)
/// is reachable, and tells callers which base URL to use RIGHT NOW - the
/// local PC when it's healthy, Render when it isn't.
///
/// This class is purely ADDITIVE and fails safe: every getter returns null
/// unless this has been started AND has an actual opinion, and null always
/// means "use your existing pre-failover URL, unchanged". A bug in here can
/// make failover not happen - it cannot break a kiosk that never calls
/// Start(), and it cannot change behavior for a kiosk whose owner-mode/health
/// state resolves to "no opinion".
///
/// Design (matches the plan doc, "מה שנשאר לעשות" -> שלב ב):
/// - ONE health check (sionyx-auth-server's /health, port 3003) stands in
///   for all three services, since they run on the same PC behind the same
///   public IP - if one answers, the others are almost certainly up too.
/// - 3 consecutive failures -> failover to Render. 3 consecutive successes
///   -> failback to local. Avoids flapping on a single dropped packet.
/// - Runs its own anonymous Firebase identity (same pattern as
///   ComputerHeartbeatService/VncRelayService) so it works from app startup,
///   independent of whether a customer is currently logged in.
/// - An owner-controlled override, read from systemSettings/failover/mode in
///   Firebase (same DB, shared across every org - see the owner dashboard's
///   Failover tab), can force "always Render" or "always local PC", bypassing
///   the health check - for when the automatic mechanism itself needs to be
///   worked around by a human.
/// - Local PC has no HTTPS yet (plan doc, Stage C not done) - Understood is
///   plain http://, and the VNC relay is plain ws:// (Render stays
///   https:// / wss:// via its managed TLS). Callers must use the scheme
///   this class returns, not assume one.
/// </summary>
public static class ServerResolver
{
    private static readonly ILogger Logger = Log.ForContext(typeof(ServerResolver));

    // Verified working externally (see plan doc) - kiosks at other sites and
    // the dashboard reach the PC through this public IP + port forwarding.
    private const string LocalHost = "83.229.22.45";
    private const int UnderstoodPort = 3001;
    private const int VncPort = 3002;
    private const int AuthPort = 3003;

    private static readonly TimeSpan CheckInterval = TimeSpan.FromSeconds(20);
    private static readonly TimeSpan HealthTimeout = TimeSpan.FromSeconds(5);
    private const int FailuresToGoRemote = 3;
    private const int SuccessesToGoLocal = 3;
    private const int SignInRetrySeconds = 30;

    private static readonly HttpClient Http = new() { Timeout = HealthTimeout };

    // Starts assuming Render (today's behavior) - only switches to local once
    // the health check has actually proven it healthy SuccessesToGoLocal times.
    private static volatile bool _localHealthy;
    private static int _consecutiveFailures;
    private static int _consecutiveSuccesses;

    // "auto" (health-check decides) | "forceRender" | "forceLocal" - owner override.
    private static volatile string _ownerMode = "auto";

    private static volatile bool _started;
    private static readonly object StartLock = new();

    /// <summary>
    /// Starts the background watcher. Safe to call multiple times or from
    /// multiple places - only the first call does anything. Call once at app
    /// startup (see SystemServicesManager.StartGlobalHotkey).
    /// </summary>
    public static void Start(FirebaseConfig config)
    {
        lock (StartLock)
        {
            if (_started) return;
            _started = true;
        }

        _ = Task.Run(() => RunAsync(config));
    }

    private static async Task RunAsync(FirebaseConfig config)
    {
        var firebase = new FirebaseClient(config);

        // Same retry-until-it-works pattern as ComputerHeartbeatService: a
        // transient failure on the very first attempt must not mean "this
        // resolver silently never does anything for the rest of the session".
        while (true)
        {
            var signIn = await firebase.SignInAnonymouslyAsync();
            if (signIn.Success) break;
            Logger.Warning("ServerResolver anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, SignInRetrySeconds);
            await Task.Delay(TimeSpan.FromSeconds(SignInRetrySeconds));
        }

        Logger.Information("ServerResolver started (checking local PC every {Seconds}s)", CheckInterval.TotalSeconds);

        while (true)
        {
            try
            {
                await RefreshOwnerModeAsync(firebase);
                await CheckHealthAsync();
            }
            catch (Exception ex)
            {
                // Never let a bug in here take down the app or freeze the
                // kiosk - worst case, state just doesn't update this cycle.
                Logger.Warning(ex, "ServerResolver check cycle failed (non-fatal)");
            }

            await Task.Delay(CheckInterval);
        }
    }

    private static async Task RefreshOwnerModeAsync(FirebaseClient firebase)
    {
        var result = await firebase.DbGetRawAsync("systemSettings/failover");
        if (!result.Success || result.Data is not JsonElement el || el.ValueKind != JsonValueKind.Object)
            return; // leave _ownerMode as it was (defaults to "auto")

        if (el.TryGetProperty("mode", out var modeEl) && modeEl.ValueKind == JsonValueKind.String)
        {
            var mode = modeEl.GetString();
            if (mode is "auto" or "forceRender" or "forceLocal")
            {
                if (_ownerMode != mode)
                    Logger.Information("ServerResolver: owner mode changed to {Mode}", mode);
                _ownerMode = mode;
            }
        }
    }

    private static async Task CheckHealthAsync()
    {
        bool healthy;
        try
        {
            using var response = await Http.GetAsync($"http://{LocalHost}:{AuthPort}/health");
            healthy = response.IsSuccessStatusCode;
        }
        catch
        {
            healthy = false;
        }

        if (healthy)
        {
            _consecutiveFailures = 0;
            _consecutiveSuccesses++;
            if (!_localHealthy && _consecutiveSuccesses >= SuccessesToGoLocal)
            {
                _localHealthy = true;
                Logger.Information("ServerResolver: local PC healthy {N}x in a row - failing back to local", SuccessesToGoLocal);
            }
        }
        else
        {
            _consecutiveSuccesses = 0;
            _consecutiveFailures++;
            if (_localHealthy && _consecutiveFailures >= FailuresToGoRemote)
            {
                _localHealthy = false;
                Logger.Warning("ServerResolver: local PC unreachable {N}x in a row - failing over to Render", FailuresToGoRemote);
            }
        }
    }

    /// <summary>Whether the local PC is the active target right now, after applying the owner override (if any).</summary>
    private static bool IsLocalActive => _ownerMode switch
    {
        "forceLocal" => true,
        "forceRender" => false,
        _ => _localHealthy,
    };

    /// <summary>
    /// Base URL for the Understood payment bridge (e.g. for CallFunctionAsync),
    /// or null if this resolver hasn't started yet or currently has no opinion -
    /// callers should fall back to their existing FunctionsBaseUrl in that case.
    /// </summary>
    public static string? GetUnderstoodBaseUrl() =>
        _started && IsLocalActive ? $"http://{LocalHost}:{UnderstoodPort}" : null;

    /// <summary>
    /// Scheme+host (no path) for the VNC relay - e.g. "ws://83.229.22.45:3002"
    /// locally or null to keep using the existing (Render, wss://) config.
    /// Local has no TLS yet, so this is intentionally plain ws:// - callers
    /// must use this string's own scheme rather than hardcoding wss://.
    /// </summary>
    public static string? GetVncRelayBaseUrl() =>
        _started && IsLocalActive ? $"ws://{LocalHost}:{VncPort}" : null;
}
