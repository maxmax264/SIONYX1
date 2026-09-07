using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Infrastructure.Logging;

namespace SionyxKiosk.Services;

/// <summary>
/// Stages 4-6 of the log-shipping feature (see ChannelLogSink for Stage 3 -
/// the always-on live stream). This service listens for dashboard-issued
/// commands, same SseListener pattern as RemoteControlReportingService:
///
///   - "logShipping/triggerAllRequested" (org-wide) - master dashboard's
///     "send logs from every kiosk now" button. Every kiosk listens on the
///     same path, so one write fans out to the whole fleet.
///   - "computers/{id}/logShipping/triggerRequested" (per-kiosk) - the
///     per-computer "send log" button next to a single machine in the list.
///   - "logShipping/intervalMs" (org-wide, legacy single-site) - dashboard's
///     frequency control; applied live via ChannelLogSink.SetIntervalMs.
///   - "logShipping/destinations" (org-wide, Stage 7 - multi-site) - a map
///     of destinationId -> { url, apiKey, intervalMs, enabled } set from
///     "הגדרות > שילוח לוגים". Applied live via ChannelLogSink.SetDestinations,
///     replacing whichever destinations were active before (including the
///     registry-based default from before this setting existed).
///
/// Both triggers do the same thing: read today's current log file off disk
/// and post its full content to the channel in chunks (a single log file
/// can exceed the channel's per-message size), independent of whatever the
/// live per-line stream is currently doing.
/// </summary>
public class LogShippingControlService
{
    private static readonly ILogger Logger = Log.ForContext<LogShippingControlService>();

    // Conservative chunk size - the channel backend imposes its own message
    // size limit that isn't documented; keeping well under any plausible
    // limit is cheaper than finding it by trial and error against a live site.
    private const int ChunkSize = 6000;

    private readonly FirebaseClient _firebase;
    private readonly string _logDir;
    private string? _computerId;
    private SseListener? _triggerAllListener;
    private SseListener? _triggerMineListener;
    private SseListener? _intervalListener;
    private SseListener? _destinationsListener;

    public LogShippingControlService(FirebaseClient firebase, string logDir)
    {
        _firebase = firebase;
        _logDir = logDir;
    }

    /// <summary>Call once at startup, after the kiosk is authenticated.</summary>
    public void Start()
    {
        _computerId = DeviceInfo.GetDeviceId();

        _triggerAllListener = _firebase.DbListen(
            "logShipping/triggerAllRequested",
            (eventType, data) => OnTriggerRequested(eventType, data, "כל הקיוסקים (כפתור מהדשבורד הראשי)"));

        _triggerMineListener = _firebase.DbListen(
            $"computers/{_computerId}/logShipping/triggerRequested",
            (eventType, data) => OnTriggerRequested(eventType, data, "קיוסק זה בלבד (כפתור פר-מחשב)"));

        _intervalListener = _firebase.DbListen(
            "logShipping/intervalMs",
            OnIntervalChanged);

        _destinationsListener = _firebase.DbListen(
            "logShipping/destinations",
            OnDestinationsChanged);
    }

    /// <summary>Parses the org's logShipping/destinations map and pushes it
    /// to the sink live. An explicitly empty/missing map means "the org
    /// hasn't configured multi-site shipping" - we intentionally do NOT
    /// touch the sink in that case, leaving whatever it started with
    /// (the registry-based single default) untouched.</summary>
    private void OnDestinationsChanged(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        if (data == null || data.Value.ValueKind != JsonValueKind.Object) return;

        var destinations = new List<(string id, string url, string apiKey, int intervalMs, bool enabled)>();
        foreach (var prop in data.Value.EnumerateObject())
        {
            try
            {
                var obj = prop.Value;
                var url = obj.TryGetProperty("url", out var u) ? u.GetString() ?? "" : "";
                if (string.IsNullOrWhiteSpace(url)) continue;
                var apiKey = obj.TryGetProperty("apiKey", out var k) ? k.GetString() ?? "" : "";
                var intervalMs = obj.TryGetProperty("intervalMs", out var im) && im.TryGetInt32(out var imVal) ? imVal : 0;
                var enabled = !obj.TryGetProperty("enabled", out var en) || en.ValueKind != JsonValueKind.False;
                destinations.Add((prop.Name, url, apiKey, intervalMs, enabled));
            }
            catch (Exception ex)
            {
                Logger.Warning(ex, "Skipping malformed log-shipping destination entry '{Id}'", prop.Name);
            }
        }

        ChannelLogSink.Current?.SetDestinations(destinations);
        Logger.Information("Log-shipping destinations applied from dashboard: {Count} site(s)", destinations.Count);
    }

    private void OnTriggerRequested(string eventType, JsonElement? data, string sourceDescription)
    {
        if (eventType != "put" || data == null) return;
        if (data.Value.ValueKind != JsonValueKind.Number) return;

        Logger.Information("Log dump requested from dashboard ({Source}) - sending current log file now", sourceDescription);
        _ = Task.Run(DumpCurrentLogFileAsync);
    }

    private void OnIntervalChanged(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        if (data.Value.ValueKind != JsonValueKind.Number) return;

        var ms = (int)data.Value.GetDouble();
        ChannelLogSink.Current?.SetIntervalMs(ms);
        Logger.Information("Log-shipping interval updated live from dashboard: {Ms}ms", ms);
    }

    private async Task DumpCurrentLogFileAsync()
    {
        var sink = ChannelLogSink.Current;
        if (sink == null)
        {
            Logger.Warning("Log dump requested but ChannelLogSink is not attached - nothing to send with");
            return;
        }

        try
        {
            var path = Path.Combine(_logDir, $"sionyx-{DateTime.Now:yyyyMMdd}.log");
            if (!File.Exists(path))
            {
                sink.SendRaw("(בקשת דמפ-לוג התקבלה, אבל עדיין אין קובץ לוג להיום)");
                return;
            }

            // FileShare.ReadWrite - Serilog's own File sink still has this
            // exact file open for writing concurrently.
            string content;
            using (var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
            using (var reader = new StreamReader(stream))
                content = await reader.ReadToEndAsync();

            if (string.IsNullOrEmpty(content))
            {
                sink.SendRaw("(קובץ הלוג של היום ריק כרגע)");
                return;
            }

            var totalChunks = (content.Length + ChunkSize - 1) / ChunkSize;
            for (var i = 0; i < content.Length; i += ChunkSize)
            {
                var chunkIndex = i / ChunkSize + 1;
                var chunk = content.Substring(i, Math.Min(ChunkSize, content.Length - i));
                var prefix = totalChunks > 1 ? $"[דמפ-לוג {chunkIndex}/{totalChunks}]\n" : "[דמפ-לוג]\n";
                sink.SendRaw(prefix + chunk);
            }

            Logger.Information("Log dump sent to channel ({Chunks} chunk(s), {Bytes} bytes)", totalChunks, content.Length);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to dump current log file to channel");
        }
    }

    public void Stop()
    {
        _triggerAllListener?.Stop();
        _triggerMineListener?.Stop();
        _intervalListener?.Stop();
        _destinationsListener?.Stop();
    }
}
