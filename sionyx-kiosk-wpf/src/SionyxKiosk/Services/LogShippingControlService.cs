using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Infrastructure.Logging;

namespace SionyxKiosk.Services;

/// <summary>
/// Dashboard control of log shipping. Everything is driven from the MASTER
/// dashboard (pc-sion.web.app/owner, "לוגים" tab) through root-level paths
/// (not per-organization), same SseListener pattern as the other services:
///
///   - systemSettings/logShipping/config - a single object
///       { autoEnabled, mode: "internal"|"external", intervalMs,
///         external: { url, apiKey, format: "sionyx"|"channel" } }
///     written whole by the bridge, applied live via ChannelLogSink.ApplyConfig.
///     autoEnabled is false by default: nothing is shipped unless the owner
///     turns it on or presses "send now".
///   - systemSettings/logShipping/triggerAll - "send now" for every kiosk.
///   - systemSettings/logShipping/triggers/{computerId} - "send now" for this
///     kiosk only.
///
/// Uses its OWN anonymous Firebase identity (like RemoteCommandService), not
/// the shared app-wide FirebaseClient: that one only holds a token while a
/// customer is logged in, so listeners built on it sit at "idle: no signed-in
/// session yet" on the login screen - exactly where a kiosk spends most of
/// its time - and the dashboard's "send now" never reached the machine.
///
/// Both triggers read today's log file off disk, post it to the active
/// destination in chunks, and flush the remembered status checklist.
///
/// Firebase replays the still-present trigger node as an initial "put" on
/// EVERY listener (re)start (app start, SSE re-auth every few hours). Each
/// trigger value is therefore remembered in the registry and ignored if seen
/// again, and a request older than MaxTriggerAge (kiosk was offline) is
/// dropped - a dump only happens when the owner actually asks for one now.
/// </summary>
public class LogShippingControlService
{
    private static readonly ILogger Logger = Log.ForContext<LogShippingControlService>();

    // Conservative chunk size - the log site imposes its own message size
    // limit that isn't documented; keeping well under any plausible limit is
    // cheaper than finding it by trial and error against a live site.
    private const int ChunkSize = 6000;

    private const string PublicLogDir = @"C:\Users\Public\Documents\SIONYX\logs";

    // Only the tail of today's log is shipped: the file can reach 10 MB, and
    // the bridge keeps just the last ~500 entries per computer anyway.
    private const int MaxDumpChars = 120_000;

    internal static readonly TimeSpan MaxTriggerAge = TimeSpan.FromMinutes(30);
    internal const string LastAllRegistryValue = "LastLogDumpAllRequestedAt";
    internal const string LastMineRegistryValue = "LastLogDumpMineRequestedAt";

    private const int SignInRetrySeconds = 30;

    private readonly FirebaseClient _firebase;
    private readonly string _logDir;
    private bool _ownsIdentity;
    private bool _starting;
    private bool _started;
    private string? _computerId;
    private SseListener? _configListener;
    private SseListener? _triggerAllListener;
    private SseListener? _triggerMineListener;

    private long _lastHandledAll;
    private long _lastHandledMine;

    /// <summary>Uses an already-built client as is (tests, or a caller that
    /// manages sign-in itself).</summary>
    public LogShippingControlService(FirebaseClient firebase, string logDir)
    {
        _firebase = firebase;
        _logDir = logDir;
    }

    /// <summary>Production: builds its own client and signs in anonymously, so
    /// it works at the idle login screen too.</summary>
    public LogShippingControlService(FirebaseConfig config, string logDir)
        : this(new FirebaseClient(config), logDir)
    {
        _ownsIdentity = true;
    }

    /// <summary>Call once at startup - does not need a customer to be logged
    /// in (see class remarks).</summary>
    public void Start()
    {
        if (_starting || _started) return;
        _computerId = DeviceInfo.GetDeviceId();

        if (!_ownsIdentity)
        {
            StartListeners();
            return;
        }

        _starting = true;
        _ = Task.Run(async () =>
        {
            try { await EnsureSignedInAndListeningAsync(); }
            finally { _starting = false; }
        });
    }

    private async Task EnsureSignedInAndListeningAsync()
    {
        var signIn = await _firebase.SignInAnonymouslyAsync();
        if (!signIn.Success)
        {
            Logger.Warning("Log-shipping anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, (int)(FirebaseClient.SignInRetryMs(SignInRetrySeconds) / 1000));
            var retryTimer = new System.Timers.Timer(FirebaseClient.SignInRetryMs(SignInRetrySeconds)) { AutoReset = false };
            retryTimer.Elapsed += async (_, _) =>
            {
                retryTimer.Dispose();
                await EnsureSignedInAndListeningAsync();
            };
            retryTimer.Start();
            return;
        }

        StartListeners();
    }

    private void StartListeners()
    {
        if (_started) return;
        _started = true;
        Logger.Information("Log-shipping control: listening on systemSettings/logShipping (config, triggerAll, triggers/{ComputerId})", _computerId);

        _configListener = _firebase.DbListen(
            "systemSettings/logShipping/config",
            OnConfigChanged,
            absolutePath: true);

        _triggerAllListener = _firebase.DbListen(
            "systemSettings/logShipping/triggerAll",
            (eventType, data) => OnTriggerRequested(eventType, data, "כל הקיוסקים", LastAllRegistryValue, ref _lastHandledAll),
            absolutePath: true);

        _triggerMineListener = _firebase.DbListen(
            $"systemSettings/logShipping/triggers/{_computerId}",
            (eventType, data) => OnTriggerRequested(eventType, data, "קיוסק זה בלבד", LastMineRegistryValue, ref _lastHandledMine),
            absolutePath: true);
    }

    private void OnConfigChanged(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        var sink = ChannelLogSink.Current;
        if (sink == null) return;

        // Config node missing/deleted -> defaults: nothing automatic, internal destination.
        if (data == null || data.Value.ValueKind == JsonValueKind.Null)
        {
            sink.ApplyConfig(false, "internal", null, null, null, 0);
            return;
        }
        if (data.Value.ValueKind != JsonValueKind.Object) return;

        try
        {
            var obj = data.Value;
            // The bridge always writes the whole object; a partial event has no
            // "mode" and must not reset the settings.
            if (!obj.TryGetProperty("mode", out var modeEl) || modeEl.ValueKind != JsonValueKind.String)
            {
                Logger.Debug("Log-shipping config event without a full object - ignored");
                return;
            }

            var autoEnabled = obj.TryGetProperty("autoEnabled", out var ae) && ae.ValueKind == JsonValueKind.True;
            var intervalMs = obj.TryGetProperty("intervalMs", out var im) && im.TryGetInt32(out var imVal) ? imVal : 0;

            string? url = null, apiKey = null, format = null;
            if (obj.TryGetProperty("external", out var ext) && ext.ValueKind == JsonValueKind.Object)
            {
                url = ext.TryGetProperty("url", out var u) && u.ValueKind == JsonValueKind.String ? u.GetString() : null;
                apiKey = ext.TryGetProperty("apiKey", out var k) && k.ValueKind == JsonValueKind.String ? k.GetString() : null;
                format = ext.TryGetProperty("format", out var f) && f.ValueKind == JsonValueKind.String ? f.GetString() : null;
            }

            sink.ApplyConfig(autoEnabled, modeEl.GetString(), url, apiKey, format, intervalMs);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Malformed log-shipping config from dashboard - ignored");
        }
    }

    private void OnTriggerRequested(string eventType, JsonElement? data, string sourceDescription, string registryValue, ref long lastHandled)
    {
        if (eventType != "put" || data == null) return;
        if (data.Value.ValueKind != JsonValueKind.Number) return;

        var requestedAt = (long)data.Value.GetDouble();
        if (requestedAt == 0) return;
        Logger.Information("Log dump trigger event received ({Source}, requestedAt={At})", sourceDescription, requestedAt);

        // Already handled in this process (SSE replay) or by a previous one
        // (the registry value survives restarts). Equality on purpose - a
        // genuinely new request always carries a different timestamp.
        var persisted = long.TryParse(RegistryConfig.ReadValueCurrentUser(registryValue), out var p) ? p : 0;
        if (requestedAt == lastHandled || requestedAt == persisted) return;

        // Remember BEFORE acting so no failure/crash can ever trigger it twice.
        lastHandled = requestedAt;
        RegistryConfig.WriteValue(registryValue, requestedAt.ToString());

        var nowMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        if (RemoteCommandService.IsStale(requestedAt, nowMs, MaxTriggerAge))
        {
            Logger.Information("Ignoring old log dump request ({Source}, requestedAt={At}) - older than {Min} min", sourceDescription, requestedAt, MaxTriggerAge.TotalMinutes);
            return;
        }

        Logger.Information("Log dump requested from dashboard ({Source}) - sending current log file now", sourceDescription);
        _ = Task.Run(DumpCurrentLogFileAsync);
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
            // Install/feature checklist first, so it shows up even if the log is empty.
            sink.FlushStatuses();

            var path = FindTodayLogFile();
            if (path == null)
            {
                sink.SendRaw("(בקשת דמפ-לוג התקבלה, אבל עדיין אין קובץ לוג להיום)", manual: true);
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
                sink.SendRaw("(קובץ הלוג של היום ריק כרגע)", manual: true);
                return;
            }

            if (content.Length > MaxDumpChars)
            {
                content = content.Substring(content.Length - MaxDumpChars);
                var nl = content.IndexOf('\n');
                if (nl >= 0 && nl < content.Length - 1) content = content.Substring(nl + 1);
                content = "(...מוצג הסוף של הלוג בלבד)\n" + content;
            }

            var totalChunks = (content.Length + ChunkSize - 1) / ChunkSize;
            for (var i = 0; i < content.Length; i += ChunkSize)
            {
                var chunkIndex = i / ChunkSize + 1;
                var chunk = content.Substring(i, Math.Min(ChunkSize, content.Length - i));
                var prefix = totalChunks > 1 ? $"[דמפ-לוג {chunkIndex}/{totalChunks}]\n" : "[דמפ-לוג]\n";
                sink.SendRaw(prefix + chunk, manual: true);
            }

            Logger.Information("Log dump sent ({Chunks} chunk(s), {Bytes} bytes)", totalChunks, content.Length);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to dump current log file");
        }
    }

    /// <summary>The newest main log written today. App.xaml.cs configures
    /// Serilog to write sionyx-yyyyMMdd.log (rolling daily, plus _001 style
    /// suffixes when a file hits its size limit) both under the user's
    /// LocalApplicationData and under C:\Users\Public\Documents\SIONYX\logs, so
    /// both are searched. The separate crash_*/errors logs are not matched.</summary>
    private string? FindTodayLogFile()
    {
        try
        {
            var today = DateTime.Now.ToString("yyyyMMdd");
            var dirs = new[] { _logDir, PublicLogDir }
                .Where(d => !string.IsNullOrWhiteSpace(d) && Directory.Exists(d))
                .Distinct(StringComparer.OrdinalIgnoreCase);

            return dirs
                .SelectMany(d => Directory.GetFiles(d, $"sionyx*{today}*.log"))
                .Where(f => !Path.GetFileName(f).Contains("errors", StringComparison.OrdinalIgnoreCase))
                .OrderByDescending(File.GetLastWriteTimeUtc)
                .FirstOrDefault();
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Could not locate the current log file");
            return null;
        }
    }

    public void Stop()
    {
        _configListener?.Stop();
        _triggerAllListener?.Stop();
        _triggerMineListener?.Stop();
    }
}
