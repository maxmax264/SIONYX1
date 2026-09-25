using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Serilog.Core;
using Serilog.Events;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Infrastructure.Logging;

/// <summary>
/// Serilog sink that ships log lines to one or more "log channel" sites
/// (e.g. the "entertainment-channel" TheChannel instance) so every kiosk's
/// logs are visible centrally instead of scattered in local files.
///
/// Stage 7 (multi-site): the org dashboard controls, per organization, WHICH
/// site(s) logs are shipped to, at what frequency each, and each site's own
/// API key - all editable/live from "הגדרות > שילוח לוגים" without a kiosk
/// restart. Config lives at organizations/{orgId}/logShipping/destinations
/// (a map of destinationId -> { url, apiKey, intervalMs, enabled }), pushed
/// to this sink live by LogShippingControlService via SetDestinations.
///
/// POST {url}/api/import/post
///   Headers: X-API-Key: {apiKey}, Content-Type: application/json
///   Body:    { "author": "<kiosk name>", "text": "...", "timestamp": ..., "is_ads": false }
///
/// Registry values (LogShipUrl/LogShipApiKey/LogShipIntervalMs) are kept as
/// the single "default" destination used until the dashboard has configured
/// any destinations for the org (or if Firebase is unreachable at startup) -
/// this preserves the exact previous single-site behavior for orgs that
/// haven't touched the new setting yet.
/// </summary>
public sealed class ChannelLogSink : ILogEventSink
{
    // entertainment-channel.onrender.com is retired (ran out of storage - it
    // kept every posted line forever with no cap/expiry). Default destination
    // is now the Understood payment bridge's /logs endpoints, backed by a
    // Redis list capped at N lines + a TTL per computer, so it cannot refill
    // the same way. Logs are read/deleted only from the owner dashboard
    // (pc-sion.web.app/owner) - there is no public viewer page anymore.
    private const string DefaultChannelUrl = "https://understood-main.onrender.com";
    private const string DefaultApiKey = "k9f2sh392zh32_secure_random_key";

    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(5) };
    private static readonly Serilog.ILogger SelfLogger = Serilog.Log.ForContext<ChannelLogSink>();

    /// <summary>The sink instance currently attached to Log.Logger, if any -
    /// lets LogShippingControlService reach it to apply live destination
    /// changes or trigger an ad-hoc send without needing its own copy of
    /// the channel URL/API key/author.</summary>
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
        /// {computerId, computerName, level, message, timestamp} body. False =
        /// legacy {url}/api/import/post TheChannel format (kept for any
        /// dashboard-configured destination that still expects it).</summary>
        public bool SionyxFormat = true;
    }

    private readonly string _author;
    private readonly string _computerId;
    private readonly object _gate = new();
    private List<Destination> _destinations;

    // Belt-and-suspenders guard against any repeating-error storm (whatever
    // the cause) hammering the Render log-ingest endpoint - independent of
    // the per-destination MinInterval throttle above, which only applies
    // when the dashboard/registry explicitly configures one (default 0).
    // Suppresses an exact repeat of the same level+text within this window;
    // does not affect distinct messages.
    private static readonly TimeSpan RepeatSuppressWindow = TimeSpan.FromSeconds(30);
    private string? _lastText;
    private DateTime _lastTextAt = DateTime.MinValue;

    static ChannelLogSink()
    {
        Http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public ChannelLogSink()
    {
        // Prefer the admin-assigned name shown in the dashboard (RegistryConfig
        // "ComputerName", set at install time / by ComputerService) so the
        // channel's "author" matches what's already familiar from the
        // computers list - falls back to the raw hostname if that's unset.
        _author = RegistryConfig.ReadValue("ComputerName", null) ?? DeviceInfo.GetComputerName();
        _computerId = DeviceInfo.GetDeviceId();

        var url = (RegistryConfig.ReadValue("LogShipUrl", DefaultChannelUrl) ?? DefaultChannelUrl).TrimEnd('/');
        var apiKey = RegistryConfig.ReadValue("LogShipApiKey", DefaultApiKey) ?? DefaultApiKey;
        var intervalMs = int.TryParse(RegistryConfig.ReadValue("LogShipIntervalMs", "0"), out var parsed) ? parsed : 0;
        var enabled = (RegistryConfig.ReadValue("LogShipEnabled", "1") ?? "1") != "0";

        _destinations = new List<Destination>
        {
            new() { Id = "default", Url = url, ApiKey = apiKey, Enabled = enabled, MinInterval = TimeSpan.FromMilliseconds(Math.Max(0, intervalMs)) },
        };

        Current = this;
    }

    /// <summary>
    /// Replaces the active destination list, applied live (no restart) -
    /// called by LogShippingControlService when the dashboard's
    /// logShipping/destinations config changes. Passing an empty list
    /// falls back to nothing being shipped (dashboard explicitly cleared
    /// all destinations) - it does NOT silently re-enable the registry
    /// default, since an explicit empty config from the dashboard means
    /// "ship nowhere".
    /// </summary>
    public void SetDestinations(IEnumerable<(string id, string url, string apiKey, int intervalMs, bool enabled)> destinations)
    {
        var list = destinations
            .Where(d => !string.IsNullOrWhiteSpace(d.url))
            .Select(d => new Destination
            {
                Id = d.id,
                Url = d.url.TrimEnd('/'),
                ApiKey = d.apiKey ?? "",
                Enabled = d.enabled,
                MinInterval = TimeSpan.FromMilliseconds(Math.Max(0, d.intervalMs)),
                // Dashboard-configured custom destinations keep the legacy
                // TheChannel format - only the built-in default targets the
                // new bridge /logs endpoints.
                SionyxFormat = false,
            })
            .ToList();

        lock (_gate)
        {
            _destinations = list;
        }
        SelfLogger.Information("Log-shipping destinations updated live: {Count} configured", list.Count);
    }

    /// <summary>Live-updates the throttle interval for a single destination
    /// (or all, if only one destination is configured) without a restart.</summary>
    public void SetIntervalMs(int ms, string? destinationId = null)
    {
        lock (_gate)
        {
            foreach (var dest in _destinations)
            {
                if (destinationId == null || dest.Id == destinationId)
                    dest.MinInterval = TimeSpan.FromMilliseconds(Math.Max(0, ms));
            }
        }
    }

    public void Emit(LogEvent logEvent)
    {
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

    /// <summary>Posts arbitrary text to every enabled destination under this
    /// kiosk's name, bypassing the throttle - used for on-demand dumps.</summary>
    public void SendRaw(string text, DateTime? timestampUtc = null)
    {
        List<Destination> snapshot;
        lock (_gate) { snapshot = _destinations; }
        foreach (var dest in snapshot)
        {
            if (dest.Enabled) SendTo(dest, text, timestampUtc ?? DateTime.UtcNow, "Information");
        }
    }

    /// <summary>Reports a one-off structured install/feature status (e.g.
    /// "tightvnc" -> installed or not) to every Sionyx-format destination's
    /// /logs/status endpoint - shown as a checklist in the owner dashboard's
    /// Logs tab, separate from the scrolling raw log tail.</summary>
    public void ReportStatus(string feature, bool success, string? message = null)
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
                    message = message ?? "",
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
