using Serilog.Core;
using Serilog.Events;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Infrastructure.Logging;

/// <summary>
/// Serilog sink that writes Warning+ events to Firebase Realtime Database.
/// Path: logs/{orgId}/{yyyyMMdd}/{timestamp}
/// </summary>
public sealed class FirebaseSink : ILogEventSink
{
    private readonly FirebaseClient _firebase;
    private readonly string _orgId;
    private readonly IFormatProvider? _formatProvider;

    public FirebaseSink(FirebaseClient firebase, string orgId, IFormatProvider? formatProvider = null)
    {
        _firebase = firebase;
        _orgId = orgId;
        _formatProvider = formatProvider;
    }

    public void Emit(LogEvent logEvent)
    {
        try
        {
            var date = logEvent.Timestamp.ToString("yyyyMMdd");
            var key = logEvent.Timestamp.ToString("HHmmss_fff");
            var path = $"logs/{_orgId}/{date}/{key}";

            var entry = new
            {
                level = logEvent.Level.ToString(),
                message = logEvent.RenderMessage(_formatProvider),
                source = logEvent.Properties.TryGetValue("SourceContext", out var src) ? src.ToString().Trim('"') : "",
                exception = logEvent.Exception?.ToString()
            };

            // Fire-and-forget — don't block the logging pipeline
            _ = _firebase.DbSetAsync(path, entry);
        }
        catch
        {
            // Sink must never throw
        }
    }
}

