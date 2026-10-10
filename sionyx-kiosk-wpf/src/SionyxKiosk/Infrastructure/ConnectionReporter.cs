using System.Net.Http;
using System.Text;
using System.Text.Json;

namespace SionyxKiosk.Infrastructure;

/// <summary>
/// Sends a small heartbeat every 15s to the SIONYX monitor service on Render
/// (see /monitor-server) so the live number of open Firebase streams per
/// machine and process can be watched on a dashboard that does not depend on
/// Firebase.
///
/// Deliberately independent of Firebase: it uses its own HttpClient, talks only
/// to the monitor URL, opens no stream and writes nothing to the database, so
/// it adds no Firebase connection and no Firebase storage. Every failure is
/// swallowed - monitoring must never affect the kiosk.
///
/// Disabled until <see cref="MonitorUrl"/> and <see cref="MonitorKey"/> are
/// filled in (or the SIONYX_MONITOR_URL / SIONYX_MONITOR_KEY environment
/// variables are set).
/// </summary>
public static class ConnectionReporter
{
    // Fill in after deploying monitor-server on Render, e.g.
    // "https://sionyx-monitor.onrender.com". Empty = reporter disabled.
    private const string MonitorUrl = "";
    private const string MonitorKey = "";

    private static readonly HttpClient s_http = new() { Timeout = TimeSpan.FromSeconds(10) };
    private static readonly DateTime s_startUtc = DateTime.UtcNow;
    private static System.Threading.Timer? s_timer;
    private static string _process = "";

    /// <summary>Optional free-text state shown on the dashboard (e.g. "idle", "session").</summary>
    public static string State { get; set; } = "";

    public static void Start(string processName)
    {
        try
        {
            var url = Environment.GetEnvironmentVariable("SIONYX_MONITOR_URL") ?? MonitorUrl;
            var key = Environment.GetEnvironmentVariable("SIONYX_MONITOR_KEY") ?? MonitorKey;
            if (string.IsNullOrWhiteSpace(url) || string.IsNullOrWhiteSpace(key) || s_timer != null) return;

            _process = processName;
            var endpoint = url.TrimEnd('/') + "/report";
            var version = System.Reflection.Assembly.GetEntryAssembly()?.GetName().Version?.ToString(3) ?? "";

            s_timer = new System.Threading.Timer(state => { _ = SendAsync(endpoint, key, version); }, null,
                TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(15));
        }
        catch
        {
            // never let monitoring affect the app
        }
    }

    private static async Task SendAsync(string endpoint, string key, string version)
    {
        try
        {
            var payload = JsonSerializer.Serialize(new
            {
                machine = Environment.MachineName,
                process = _process,
                version,
                state = State,
                sse = SseListener.ConnectedCount,
                paths = SseListener.ConnectedPaths(),
                attempts = SseListener.Attempts,
                uptimeSec = (int)(DateTime.UtcNow - s_startUtc).TotalSeconds,
            });

            using var req = new HttpRequestMessage(HttpMethod.Post, endpoint)
            {
                Content = new StringContent(payload, Encoding.UTF8, "application/json"),
            };
            req.Headers.Add("x-report-key", key);
            using var resp = await s_http.SendAsync(req);
        }
        catch
        {
            // monitor unreachable / Render asleep: ignore
        }
    }
}
