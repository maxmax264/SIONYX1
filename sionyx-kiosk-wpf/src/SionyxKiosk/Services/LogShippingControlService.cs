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
///   - "logShipping/intervalMs" (org-wide) - dashboard's frequency control;
///     applied live via ChannelLogSink.SetIntervalMs, no restart needed.
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
    }
}
