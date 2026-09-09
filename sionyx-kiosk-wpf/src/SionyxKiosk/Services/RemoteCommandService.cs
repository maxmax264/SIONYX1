using System.Diagnostics;
using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

/// <summary>
/// Listens for dashboard-issued power commands (shutdown / restart) on
/// "computers/{id}/powerCommand/requested", same SseListener pattern as
/// RemoteControlReportingService and LogShippingControlService. Runs the
/// Windows `shutdown.exe` utility, reports the outcome to
/// "computers/{id}/powerCommand/lastResult", then clears "requested" so
/// the same command isn't re-applied on the next SSE reconnect (Firebase
/// replays existing data as an initial "put" when a listener (re)starts).
/// </summary>
public class RemoteCommandService
{
    private static readonly ILogger Logger = Log.ForContext<RemoteCommandService>();

    private readonly FirebaseClient _firebase;
    private string? _computerId;
    private SseListener? _listener;

    // Guards against acting twice on the same command - e.g. the SSE
    // stream reconnecting and Firebase replaying the still-present
    // "requested" node as a fresh "put" event before our own delete of it
    // round-trips.
    private long _lastHandledRequestedAt;

    public RemoteCommandService(FirebaseClient firebase)
    {
        _firebase = firebase;
    }

    /// <summary>Call once at startup, after the kiosk is authenticated.</summary>
    public void Start()
    {
        _computerId = DeviceInfo.GetDeviceId();
        _listener = _firebase.DbListen(
            $"computers/{_computerId}/powerCommand/requested",
            OnCommandRequested);
    }

    private void OnCommandRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        if (data == null || data.Value.ValueKind != JsonValueKind.Object) return;

        var obj = data.Value;
        var type = obj.TryGetProperty("type", out var t) ? t.GetString() : null;
        var requestedAt = obj.TryGetProperty("requestedAt", out var r) && r.TryGetInt64(out var ra) ? ra : 0;

        if (string.IsNullOrEmpty(type) || requestedAt == 0) return;
        if (requestedAt == _lastHandledRequestedAt) return; // already handled (SSE replay)
        _lastHandledRequestedAt = requestedAt;

        if (type != "shutdown" && type != "restart")
        {
            Logger.Warning("Unknown power command type '{Type}' - ignoring", type);
            return;
        }

        Logger.Warning("Power command received from dashboard: {Type}", type);
        _ = Task.Run(() => ExecuteAsync(type));
    }

    private async Task ExecuteAsync(string type)
    {
        try
        {
            await ReportResultAsync(type, "executing");

            // /t 5 gives a few seconds for the result write above and any
            // in-flight Firebase calls (heartbeat, etc.) to flush before
            // Windows tears the process down.
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
            await ClearRequestedAsync();
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Failed to execute power command '{Type}'", type);
            await ReportResultAsync(type, "failed: " + ex.Message);
        }
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
            await _firebase.DbDeleteAsync($"computers/{_computerId}/powerCommand/requested");
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
