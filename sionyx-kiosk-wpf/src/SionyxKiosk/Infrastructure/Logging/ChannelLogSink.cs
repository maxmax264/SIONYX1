using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Serilog.Core;
using Serilog.Events;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Services;

namespace SionyxKiosk.Infrastructure.Logging;

/// <summary>
/// Serilog sink that ships log lines to a central log site so every kiosk's
/// logs are visible in one place instead of scattered in local files.
///
/// NOTHING IS SENT AUTOMATICALLY BY DEFAULT. The master dashboard
/// (pc-sion.web.app/owner, "לוגים" tab) controls everything through
/// systemSettings/logShipping/config, pushed live by LogShippingControlService
/// via ApplyConfig:
///   - autoEnabled (default false): when false, the live per-line stream, the
///     hourly "alive" line and the automatic status reports are all silent.
///     Logs leave the machine ONLY when the dashboard presses a "send now"
///     button (SendRaw(..., manual: true) / FlushStatuses).
///   - mode "internal" (default): the Understood bridge's /logs endpoints
///     (Redis-backed ring buffer, read from the owner dashboard).
///   - mode "external": a custom site (url + apiKey + format), either the
///     Sionyx bridge format or the legacy TheChannel format.
///
/// Registry values (LogShipUrl/LogShipApiKey) still define the internal
/// destination. LogShipEnabled=0 in the registry is a hard local kill switch:
/// this kiosk then never ships anything, whatever the dashboard says.
///
/// Sionyx format: POST {url}/logs/ingest  (X-API-Key)
///   Body: { computerId, computerName, level, message, timestamp }
/// Channel format: POST {url}/api/import/post  (X-API-Key)
///   Body: { author, text, timestamp, is_ads: false }
/// </summary>
public sealed class ChannelLogSink : ILogEventSink
{
    // Default (internal) destination: the Understood payment bridge's /logs
    // endpoints, backed by a Redis list capped at N lines + a TTL per
    // computer, so it cannot fill storage over time. Logs are read/deleted
    // only from the owner dashboard (pc-sion.web.app/owner).
    private const string DefaultChannelUrl = "https://understood-main.onrender.com";
    private const string DefaultApiKey = "k9f2sh392zh32_secure_random_key";

    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(5) };
    private static readonly Serilog.ILogger SelfLogger = Serilog.Log.ForContext<ChannelLogSink>();

    /// <summary>The sink instance currently attached to Log.Logger, if any -
    /// lets LogShippingControlService reach it to apply dashboard config or
    /// trigger an on-demand send.</summary>
    public static ChannelLogSink? Current { get; private set; }

    private sealed class Destination
    {
        public required string Id;
        public required string Url;
        public required string ApiKey;
        public bool Enabled = true;
        public TimeSpan MinInterval;
        public DateTime LastSentAt = DateTime.MinValue;
        /// <summary>True = POST {url}/logs/ingest with the Understood bridge's
        /// body. False = legacy {url}/api/import/post TheChannel format.</summary>
        public bool SionyxFormat = true;
    }

    // Resolved on every send (not cached at construction) so a dashboard rename
    // shows up in the owner logs list within one heartbeat, without a restart.
    // Same priority as AuthViewModel.ComputerName: HKCU dashboard name,
    // then HKLM install-time name, then the Windows hostname.
    private static string _author =>
        RegistryConfig.ReadValueCurrentUser(ComputerHeartbeatService.DashboardNameValue) is { } d && !string.IsNullOrWhiteSpace(d)
            ? d
            : RegistryConfig.ReadValue("ComputerName", null) ?? DeviceInfo.GetComputerName();
    private readonly string _computerId;
    private readonly object _gate = new();
    private List<Destination> _destinations;

    // Automatic shipping (live stream, hourly alive line, status reports).
    // OFF until the dashboard explicitly turns it on.
    private volatile bool _autoEnabled;
    // Local registry kill switch (LogShipEnabled=0) - blocks every send.
    private readonly bool _hardDisabled;

    // Latest structured status per feature - always remembered, but only sent
    // automatically when _autoEnabled; FlushStatuses sends them on demand.
    private readonly Dictionary<string, (bool success, string message)> _lastStatuses = new();

    // Belt-and-suspenders guard against any repeating-error storm hammering the
    // log endpoint: suppresses an exact repeat of the same level+text within
    // this window; does not affect distinct messages.
    private static readonly TimeSpan RepeatSuppressWindow = TimeSpan.FromSeconds(30);
    private string? _lastText;
    private DateTime _lastTextAt = DateTime.MinValue;

    static ChannelLogSink()
    {
        Http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public ChannelLogSink()
    {
        _computerId = DeviceInfo.GetDeviceId();
        _hardDisabled = (RegistryConfig.ReadValue("LogShipEnabled", "1") ?? "1") == "0";
        _autoEnabled = false;
        _destinations = new List<Destination> { BuildInternalDestination(0) };

        Current = this;
    }

    private static Destination BuildInternalDestination(int intervalMs)
    {
        var url = (RegistryConfig.ReadValue("LogShipUrl", DefaultChannelUrl) ?? DefaultChannelUrl).TrimEnd('/');
        var apiKey = RegistryConfig.ReadValue("LogShipApiKey", DefaultApiKey) ?? DefaultApiKey;
        return new Destination
        {
            Id = "internal",
            Url = url,
            ApiKey = apiKey,
            MinInterval = TimeSpan.FromMilliseconds(Math.Max(0, intervalMs)),
        };
    }

    /// <summary>
    /// Applies the dashboard's log-shipping config live (no restart).
    /// mode "external" with a non-empty url ships to that site; anything else
    /// ships to the internal Understood bridge. <paramref name="autoEnabled"/>
    /// only controls the AUTOMATIC stream - manual "send now" always works.
    /// </summary>
    public void ApplyConfig(bool autoEnabled, string? mode, string? url, string? apiKey, string? format, int intervalMs)
    {
        Destination dest;
        var external = string.Equals(mode, "external", StringComparison.OrdinalIgnoreCase)
                       && !string.IsNullOrWhiteSpace(url);
        if (external)
        {
            dest = new Destination
            {
                Id = "external",
                Url = url!.Trim().TrimEnd('/'),
                ApiKey = apiKey ?? "",
                MinInterval = TimeSpan.FromMilliseconds(Math.Max(0, intervalMs)),
                SionyxFormat = !string.Equals(format, "channel", StringComparison.OrdinalIgnoreCase),
            };
        }
        else
        {
            dest = BuildInternalDestination(intervalMs);
        }

        lock (_gate)
        {
            _destinations = new List<Destination> { dest };
        }
        _autoEnabled = autoEnabled;
        SelfLogger.Information(
            "Log-shipping config applied from dashboard: auto={Auto}, mode={Mode}, format={Format}",
            autoEnabled, external ? "external" : "internal", dest.SionyxFormat ? "sionyx" : "channel");
    }

    public void Emit(LogEvent logEvent)
    {
        // Automatic stream is opt-in from the dashboard.
        if (_hardDisabled || !_autoEnabled) return;

        var text = FormatText(logEvent);
        var timestamp = logEvent.Timestamp.UtcDateTime;
        var level = logEvent.Level.ToString();

        lock (_gate)
        {
            var now = DateTime.UtcNow;
            if (text == _lastText && now - _lastTextAt < RepeatSuppressWindow)
                return;
            _lastText = text;
            _lastTextAt = now;
        }

        List<Destination> snapshot;
        lock (_gate) { snapshot = _destinations; }

        foreach (var dest in snapshot)
        {
            if (!dest.Enabled) continue;

            lock (_gate)
            {
                if (dest.MinInterval > TimeSpan.Zero)
                {
                    var now = DateTime.UtcNow;
                    if (now - dest.LastSentAt < dest.MinInterval) continue;
                    dest.LastSentAt = now;
                }
            }

            SendTo(dest, text, timestamp, level);
        }
    }

    /// <summary>Posts arbitrary text to the active destination under this
    /// kiosk's name, bypassing the throttle. <paramref name="manual"/> = true
    /// for dashboard-requested dumps (always sent); the default (false) is for
    /// automatic lines such as the periodic "alive" message, which are only
    /// sent while automatic shipping is enabled.</summary>
    public void SendRaw(string text, DateTime? timestampUtc = null, bool manual = false)
    {
        if (_hardDisabled) return;
        if (!manual && !_autoEnabled) return;

        List<Destination> snapshot;
        lock (_gate) { snapshot = _destinations; }
        foreach (var dest in snapshot)
        {
            if (dest.Enabled) SendTo(dest, text, timestampUtc ?? DateTime.UtcNow, "Information");
        }
    }

    /// <summary>Records a one-off structured install/feature status (e.g.
    /// "tightvnc" -> installed or not). Sent to the owner dashboard's checklist
    /// only while automatic shipping is enabled; otherwise just remembered
    /// until FlushStatuses (manual "send now").</summary>
    public void ReportStatus(string feature, bool success, string? message = null)
    {
        lock (_gate) { _lastStatuses[feature] = (success, message ?? ""); }
        if (_hardDisabled || !_autoEnabled) return;
        SendStatusToAll(feature, success, message ?? "");
    }

    /// <summary>Sends every remembered status now (manual "send now").</summary>
    public void FlushStatuses()
    {
        if (_hardDisabled) return;
        KeyValuePair<string, (bool success, string message)>[] copy;
        lock (_gate) { copy = _lastStatuses.ToArray(); }
        foreach (var kv in copy)
            SendStatusToAll(kv.Key, kv.Value.success, kv.Value.message);
    }

    private void SendStatusToAll(string feature, bool success, string message)
    {
        List<Destination> snapshot;
        lock (_gate) { snapshot = _destinations; }

        foreach (var dest in snapshot)
        {
            if (!dest.Enabled || !dest.SionyxFormat) continue;
            try
            {
                var body = JsonSerializer.Serialize(new
                {
                    computerId = _computerId,
                    computerName = _author,
                    feature,
                    success,
                    message,
                });
                var request = new HttpRequestMessage(HttpMethod.Post, $"{dest.Url}/logs/status")
                {
                    Content = new StringContent(body, Encoding.UTF8, "application/json"),
                };
                request.Headers.Add("X-API-Key", dest.ApiKey);
                _ = Http.SendAsync(request).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        SelfLogger.Debug(t.Exception, "Status report to {DestId} failed (non-fatal)", dest.Id);
                }, TaskContinuationOptions.OnlyOnFaulted);
            }
            catch
            {
                // Never throw
            }
        }
    }

    private void SendTo(Destination dest, string text, DateTime timestampUtc, string level)
    {
        try
        {
            string body;
            string path;
            if (dest.SionyxFormat)
            {
                body = JsonSerializer.Serialize(new
                {
                    computerId = _computerId,
                    computerName = _author,
                    level,
                    message = text,
                    timestamp = timestampUtc,
                });
                path = "/logs/ingest";
            }
            else
            {
                body = JsonSerializer.Serialize(new
                {
                    author = _author,
                    text,
                    timestamp = timestampUtc,
                    is_ads = false,
                });
                path = "/api/import/post";
            }

            var request = new HttpRequestMessage(HttpMethod.Post, $"{dest.Url}{path}")
            {
                Content = new StringContent(body, Encoding.UTF8, "application/json"),
            };
            request.Headers.Add("X-API-Key", dest.ApiKey);

            // Fire-and-forget - a sink must never block or throw back into
            // the logging pipeline. Failures are swallowed here on purpose:
            // logging the failure to this same sink would recurse.
            _ = Http.SendAsync(request).ContinueWith(t =>
            {
                if (t.IsFaulted)
                    SelfLogger.Debug(t.Exception, "Channel log ship to {DestId} failed (non-fatal)", dest.Id);
            }, TaskContinuationOptions.OnlyOnFaulted);
        }
        catch
        {
            // Sink must never throw
        }
    }

    private static string FormatText(LogEvent logEvent)
    {
        var source = logEvent.Properties.TryGetValue("SourceContext", out var src)
            ? src.ToString().Trim('"')
            : "";
        var message = logEvent.RenderMessage();
        var line = $"**[{logEvent.Level}]** `{source}` {message}";
        if (logEvent.Exception != null)
            line += $"\n```\n{logEvent.Exception}\n```";
        return line;
    }
}
