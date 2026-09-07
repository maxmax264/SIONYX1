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
    private const string DefaultChannelUrl = "https://entertainment-channel.onrender.com";
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
    }

    private readonly string _author;
    private readonly object _gate = new();
    private List<Destination> _destinations;

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

            SendTo(dest, text, timestamp);
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
            if (dest.Enabled) SendTo(dest, text, timestampUtc ?? DateTime.UtcNow);
        }
    }

    private void SendTo(Destination dest, string text, DateTime timestampUtc)
    {
        try
        {
            var body = JsonSerializer.Serialize(new
            {
                author = _author,
                text,
                timestamp = timestampUtc,
                is_ads = false,
            });

            var request = new HttpRequestMessage(HttpMethod.Post, $"{dest.Url}/api/import/post")
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
