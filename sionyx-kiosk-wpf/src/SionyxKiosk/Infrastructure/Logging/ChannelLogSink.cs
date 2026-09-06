using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Serilog.Core;
using Serilog.Events;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Infrastructure.Logging;

/// <summary>
/// Serilog sink that ships log lines to the "entertainment-channel" site
/// (a repurposed TheChannel broadcast-channel instance used as a live log
/// viewer - see backend/api.go in that repo) so every kiosk's logs are
/// visible in one place instead of scattered in local files.
///
/// POST {ChannelUrl}/api/import/post
///   Headers: X-API-Key: {ApiKey}, Content-Type: application/json
///   Body:    { "author": "<kiosk name>", "text": "...", "timestamp": ..., "is_ads": false }
///
/// "author" is what the dashboard/channel shows as the message source, so
/// it's set to the kiosk's own name (RegistryConfig "ComputerName", falling
/// back to the machine's hostname) - this is how a reader tells which kiosk
/// a given line came from.
///
/// Frequency control (Stage 3 scope - a Firebase-driven live toggle is a
/// later stage): reads registry values so an installer/admin can dial this
/// down without a rebuild.
///   - LogShipEnabled     ("0"/"1", default "1")
///   - LogShipIntervalMs  (minimum ms between two posts; default "0" = no
///                          throttle, ship every line immediately - this
///                          matches "as fast as possible" for active dev)
/// Minimum log level to ship is set where the sink is attached (App.xaml.cs),
/// via Serilog's own restrictedToMinimumLevel - also registry-overridable
/// there (LogShipMinLevel).
/// </summary>
public sealed class ChannelLogSink : ILogEventSink
{
    // Defaults match what's already configured on the entertainment-channel
    // Render deployment. Override via registry (see class comment) if the
    // site or key ever changes without a rebuild.
    private const string DefaultChannelUrl = "https://entertainment-channel.onrender.com";
    private const string DefaultApiKey = "k9f2sh392zh32_secure_random_key";

    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(5) };
    private static readonly Serilog.ILogger SelfLogger = Serilog.Log.ForContext<ChannelLogSink>();

    private readonly string _channelUrl;
    private readonly string _apiKey;
    private readonly string _author;
    private readonly TimeSpan _minInterval;
    private readonly object _gate = new();
    private DateTime _lastSentAt = DateTime.MinValue;

    static ChannelLogSink()
    {
        Http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public ChannelLogSink()
    {
        _channelUrl = (RegistryConfig.ReadValue("LogShipUrl", DefaultChannelUrl) ?? DefaultChannelUrl).TrimEnd('/');
        _apiKey = RegistryConfig.ReadValue("LogShipApiKey", DefaultApiKey) ?? DefaultApiKey;

        var intervalMs = int.TryParse(RegistryConfig.ReadValue("LogShipIntervalMs", "0"), out var parsed) ? parsed : 0;
        _minInterval = TimeSpan.FromMilliseconds(Math.Max(0, intervalMs));

        // Prefer the admin-assigned name shown in the dashboard (RegistryConfig
        // "ComputerName", set at install time / by ComputerService) so the
        // channel's "author" matches what's already familiar from the
        // computers list - falls back to the raw hostname if that's unset.
        _author = RegistryConfig.ReadValue("ComputerName", null) ?? DeviceInfo.GetComputerName();
    }

    public bool Enabled => (RegistryConfig.ReadValue("LogShipEnabled", "1") ?? "1") != "0";

    public void Emit(LogEvent logEvent)
    {
        if (!Enabled) return;

        // Throttle: if an interval is configured, drop events that arrive
        // faster than it rather than queuing them - this is a live tail of
        // "what's happening now", not an audit log that needs every line.
        if (_minInterval > TimeSpan.Zero)
        {
            lock (_gate)
            {
                var now = DateTime.UtcNow;
                if (now - _lastSentAt < _minInterval) return;
                _lastSentAt = now;
            }
        }

        try
        {
            var text = FormatText(logEvent);

            var body = JsonSerializer.Serialize(new
            {
                author = _author,
                text,
                timestamp = logEvent.Timestamp.UtcDateTime,
                is_ads = false,
            });

            var request = new HttpRequestMessage(HttpMethod.Post, $"{_channelUrl}/api/import/post")
            {
                Content = new StringContent(body, Encoding.UTF8, "application/json"),
            };
            request.Headers.Add("X-API-Key", _apiKey);

            // Fire-and-forget - a sink must never block or throw back into
            // the logging pipeline. Failures are swallowed here on purpose:
            // logging the failure to this same sink would recurse.
            _ = Http.SendAsync(request).ContinueWith(t =>
            {
                if (t.IsFaulted)
                    SelfLogger.Debug(t.Exception, "Channel log ship failed (non-fatal)");
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
