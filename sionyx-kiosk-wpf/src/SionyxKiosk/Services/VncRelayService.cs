using System.IO;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Text.Json;
using Serilog;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Services;

/// <summary>
/// On a dashboard request, bridges the kiosk's local TightVNC server
/// (127.0.0.1:5900, never exposed on the LAN) to the sionyx-vnc-relay
/// WebSocket relay, so an admin's browser (noVNC) can view/control the
/// kiosk screen without needing a public IP, port-forwarding, or any
/// remote-control client that would collide with NetFree's TLS
/// interception (see RemoteControlReportingService's RustDesk/AnyDesk
/// findings - this deliberately avoids that whole class of problem by
/// using plain WebSocket-over-TLS, same as the rest of this app's
/// Firebase/Understood-bridge traffic).
///
/// Listens on "computers/{id}/vncRelay/requested" - same
/// listen-then-clear pattern as RemoteCommandService, so an SSE
/// reconnect never re-triggers an already-handled session.
/// </summary>
public class VncRelayService
{
    private static readonly ILogger Logger = Log.ForContext<VncRelayService>();

    // Override via registry value "VncRelayUrl" if the Render service
    // ends up on a different subdomain than this default.
    private const string DefaultRelayHost = "sionyx-vnc-relay.onrender.com";
    private const string VncHost = "127.0.0.1";
    private const int VncPort = 5900;
    private static readonly TimeSpan MaxSessionDuration = TimeSpan.FromMinutes(30);

    private readonly FirebaseClient _firebase;
    private string? _computerId;
    private SseListener? _listener;
    private CancellationTokenSource? _activeSessionCts;
    private long _lastHandledRequestedAt;

    public VncRelayService(FirebaseClient firebase)
    {
        _firebase = firebase;
    }

    /// <summary>Call once at startup, after the kiosk is authenticated.</summary>
    public void Start()
    {
        _computerId = DeviceInfo.GetDeviceId();
        _listener = _firebase.DbListen(
            $"computers/{_computerId}/vncRelay/requested",
            OnSessionRequested);
    }

    public void Stop()
    {
        _listener?.Stop();
        _activeSessionCts?.Cancel();
    }

    private void OnSessionRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        if (data == null || data.Value.ValueKind != JsonValueKind.Object) return;

        var obj = data.Value;
        var token = obj.TryGetProperty("token", out var t) ? t.GetString() : null;
        var requestedAt = obj.TryGetProperty("requestedAt", out var r) && r.TryGetInt64(out var ra) ? ra : 0;

        if (string.IsNullOrWhiteSpace(token) || requestedAt == 0) return;
        if (requestedAt == _lastHandledRequestedAt) return; // SSE replay of the same request
        _lastHandledRequestedAt = requestedAt;

        Logger.Warning("VNC session requested from dashboard (token {Token}...)", token[..Math.Min(6, token.Length)]);

        // A new request replaces any session still running.
        _activeSessionCts?.Cancel();
        var cts = new CancellationTokenSource(MaxSessionDuration);
        _activeSessionCts = cts;
        _ = Task.Run(() => RunSessionAsync(token, cts.Token));
    }

    private async Task RunSessionAsync(string token, CancellationToken ct)
    {
        var relayHost = RegistryConfig.ReadValue("VncRelayUrl", DefaultRelayHost)!.Trim().TrimEnd('/');
        relayHost = relayHost.Replace("https://", "").Replace("wss://", "").Replace("http://", "");
        var relayUri = new Uri($"wss://{relayHost}/agent/{Uri.EscapeDataString(token)}");

        using var ws = new ClientWebSocket();
        using var tcp = new TcpClient();

        try
        {
            await ws.ConnectAsync(relayUri, ct);
            Logger.Information("VNC relay WebSocket connected to {Host}", relayHost);

            await tcp.ConnectAsync(VncHost, VncPort, ct);
            Logger.Information("Connected to local VNC server on {Host}:{Port}", VncHost, VncPort);

            await ReportResultAsync("connected");
            await ClearRequestedAsync();

            var netStream = tcp.GetStream();
            var wsToTcp = PumpWebSocketToTcpAsync(ws, netStream, ct);
            var tcpToWs = PumpTcpToWebSocketAsync(netStream, ws, ct);
            await Task.WhenAny(wsToTcp, tcpToWs);
        }
        catch (SocketException ex)
        {
            Logger.Warning(ex, "Could not reach local VNC server on {Host}:{Port} - is TightVNC installed and running?", VncHost, VncPort);
            await ReportResultAsync("failed: no local VNC server on " + VncPort);
        }
        catch (OperationCanceledException)
        {
            Logger.Information("VNC relay session ended (cancelled/timed out)");
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "VNC relay session failed");
            await ReportResultAsync("failed: " + ex.Message);
        }
        finally
        {
            try { if (ws.State == WebSocketState.Open) await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "done", CancellationToken.None); }
            catch { /* best effort */ }
            await ReportResultAsync("ended");
        }
    }

    private static async Task PumpWebSocketToTcpAsync(ClientWebSocket ws, Stream tcp, CancellationToken ct)
    {
        var buffer = new byte[16 * 1024];
        while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            var result = await ws.ReceiveAsync(buffer, ct);
            if (result.MessageType == WebSocketMessageType.Close) break;
            if (result.Count > 0) await tcp.WriteAsync(buffer, 0, result.Count, ct);
        }
    }

    private static async Task PumpTcpToWebSocketAsync(Stream tcp, ClientWebSocket ws, CancellationToken ct)
    {
        var buffer = new byte[16 * 1024];
        while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            var read = await tcp.ReadAsync(buffer, 0, buffer.Length, ct);
            if (read == 0) break; // remote closed the VNC connection
            await ws.SendAsync(new ArraySegment<byte>(buffer, 0, read), WebSocketMessageType.Binary, true, ct);
        }
    }

    private async Task ReportResultAsync(string status)
    {
        try
        {
            await _firebase.DbUpdateAsync($"computers/{_computerId}/vncRelay", new Dictionary<string, object>
            {
                ["lastResult"] = new { status, at = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() },
            });
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to report VNC session result (non-fatal)");
        }
    }

    private async Task ClearRequestedAsync()
    {
        try
        {
            await _firebase.DbDeleteAsync($"computers/{_computerId}/vncRelay/requested");
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to clear vncRelay/requested (non-fatal)");
        }
    }
}
