using System.Text.Json;
using Serilog;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Low-cost alternative to <see cref="SseListener"/> for nodes that change
/// rarely and do not need sub-second delivery (dashboard-issued power
/// commands, log-shipping config/triggers).
///
/// Why: every SseListener is a permanent open connection to Firebase, and
/// Firebase's free plan caps simultaneous connections (~100). With ~9 SSE
/// streams per kiosk that cap is reached with about a dozen machines. A poll
/// is a short GET that does not stay open, so it does not count toward the
/// limit.
///
/// Behaviour mirrors what SSE gave the callers: the callback fires once with
/// the current value, and again only when the node's JSON text changes. The
/// callbacks (RemoteCommandService, LogShippingControlService) already de-dupe
/// by requestedAt, so an extra delivery is harmless.
/// </summary>
public sealed class DbPoller : IDisposable
{
    private static readonly ILogger Logger = Log.ForContext<DbPoller>();

    private readonly FirebaseClient _firebase;
    private readonly string _path;
    private readonly bool _absolutePath;
    private readonly TimeSpan _interval;
    private readonly TimeSpan _maxInitialDelay;
    private readonly Action<JsonElement?> _onChange;

    private CancellationTokenSource? _cts;
    private string? _lastRaw;

    /// <summary>Number of poll loops currently running in this process (diagnostics/tests).</summary>
    private static int s_active;
    public static int ActiveCount => Volatile.Read(ref s_active);

    public bool IsRunning => _cts != null && !_cts.IsCancellationRequested;

    internal DbPoller(
        FirebaseClient firebase,
        string path,
        bool absolutePath,
        TimeSpan interval,
        Action<JsonElement?> onChange,
        TimeSpan? maxInitialDelay = null)
    {
        _firebase = firebase;
        _path = path;
        _absolutePath = absolutePath;
        _interval = interval;
        _maxInitialDelay = maxInitialDelay ?? TimeSpan.FromSeconds(5);
        _onChange = onChange;
    }

    internal void Start()
    {
        if (IsRunning) return;
        var cts = new CancellationTokenSource();
        _cts = cts;
        _ = Task.Run(() => LoopAsync(cts.Token));
        Logger.Information("DB poller started for {Path} (every {Seconds}s)", _path, (int)_interval.TotalSeconds);
    }

    public void Stop()
    {
        var cts = _cts;
        _cts = null;
        if (cts == null) return;
        try { cts.Cancel(); } catch (ObjectDisposedException) { }
        cts.Dispose();
        Logger.Information("DB poller stopped for {Path}", _path);
    }

    public void Dispose() => Stop();

    private async Task LoopAsync(CancellationToken ct)
    {
        Interlocked.Increment(ref s_active);
        try
        {
            // Spread the first poll so a room of kiosks that boot together
            // does not hit Firebase in the same second.
            if (_maxInitialDelay > TimeSpan.Zero)
            {
                var first = TimeSpan.FromMilliseconds(Random.Shared.NextDouble() * _maxInitialDelay.TotalMilliseconds);
                await Task.Delay(first, ct);
            }

            while (!ct.IsCancellationRequested)
            {
                await PollOnceAsync(ct);

                // +-20% jitter on every cycle keeps the kiosks de-synchronised.
                var jitter = 0.8 + Random.Shared.NextDouble() * 0.4;
                await Task.Delay(TimeSpan.FromMilliseconds(_interval.TotalMilliseconds * jitter), ct);
            }
        }
        catch (OperationCanceledException)
        {
            // Normal on Stop().
        }
        finally
        {
            Interlocked.Decrement(ref s_active);
        }
    }

    internal async Task PollOnceAsync(CancellationToken ct)
    {
        var raw = await _firebase.DbReadRawJsonQuietAsync(_path, _absolutePath, ct);
        if (raw == null) return;                 // failed read - try again next cycle
        if (raw == _lastRaw) return;             // unchanged since last delivery
        _lastRaw = raw;

        try
        {
            var value = JsonSerializer.Deserialize<JsonElement>(raw);
            _onChange(value);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "DB poller callback failed for {Path}", _path);
        }
    }
}
