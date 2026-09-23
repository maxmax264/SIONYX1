using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Net.Security;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.ServiceProcess;
using System.Text;
using System.Text.Json;
using Microsoft.Win32;
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
///
/// Uses its OWN anonymous Firebase identity (like ComputerHeartbeatService),
/// not the shared app-wide FirebaseClient. That shared client only ever
/// holds a token while an actual customer is logged in on the kiosk -
/// this listener needs to work at any time (including the idle login
/// screen), so it can't depend on that. Bug found in the field: this used
/// to take the shared FirebaseClient and every SSE reconnect attempted
/// while no customer was logged in failed with "Not authenticated" and
/// never recovered until someone happened to log in.
/// </summary>
public class VncRelayService
{
    private static readonly ILogger Logger = Log.ForContext<VncRelayService>();

    // Override via registry value "VncRelayUrl" if the Render service
    // ends up on a different subdomain than this default.
    private const string DefaultRelayHost = "sionyx-vnc-relaymain.onrender.com";
    private const string VncHost = "127.0.0.1";
    private const int VncPort = 5900;
    private const string TightVncExePath = @"C:\Program Files\TightVNC\tvnserver.exe";
    private static readonly TimeSpan MaxSessionDuration = TimeSpan.FromMinutes(30);
    private const int SignInRetrySeconds = 30;
    // Firebase SSE keep-alives arrive roughly every 15-20s when a stream is
    // healthy, so 5 minutes of total silence on this specific listener is a
    // strong signal it has gone quietly dead (observed live, 14/09/2026: a
    // listener stopped receiving anything - no errors, no reconnect logs,
    // nothing - for 2.5+ hours, until the whole app was restarted by hand).
    private static readonly TimeSpan ListenerStaleThreshold = TimeSpan.FromMinutes(5);

    // A second, different failure mode found the same day (14/09/2026,
    // investigated after "another model" ran manual field debugging): the
    // keep-alive channel itself can keep flowing forever while the
    // underlying subscription for *real* put/patch events silently dies on
    // the same connection - LastEventUtc keeps refreshing off the
    // keep-alives, so ListenerStaleThreshold never fires, even though a
    // pending VNC request just sits unhandled in Firebase indefinitely.
    //
    // This can't be fixed by watching for "too long since the last real
    // event" instead, because a legitimately idle listener (nobody has
    // requested VNC in a while - completely normal, can be hours) looks
    // identical to a silently-broken one by that measure alone; either
    // heuristic would either miss the real failure or restart constantly on
    // healthy idle kiosks. So instead of trying to detect this state at all,
    // the listener is unconditionally cycled on a fixed schedule - bounding
    // how long a zombie stream can go unnoticed to this interval, regardless
    // of what its keep-alives claim.
    private static readonly TimeSpan PeriodicReconnectInterval = TimeSpan.FromMinutes(10);
    private DateTime _listenerStartedUtc = DateTime.UtcNow;

    private readonly FirebaseClient _firebase;
    private string? _computerId;
    private SseListener? _listener;
    private System.Timers.Timer? _watchdogTimer;
    private CancellationTokenSource? _activeSessionCts;
    private long _lastHandledRequestedAt;
    private bool _starting;
    private bool _signedIn;

    public VncRelayService(FirebaseConfig config)
    {
        _firebase = new FirebaseClient(config);
    }

    /// <summary>Call once at startup - does not need the kiosk to be authenticated
    /// (see class remarks: this keeps its own anonymous identity).</summary>
    public void Start()
    {
        if (_starting || _signedIn) return;
        _computerId = DeviceInfo.GetDeviceId();

        // Launch tvnserver in THIS session (the kiosk's own interactive
        // session) rather than relying on a Windows service - a service
        // runs in Session 0 and would only ever see a black screen, not
        // the actual kiosk desktop. install-tightvnc.ps1 deliberately
        // does not register tvnserver as a service for this reason.
        EnsureTightVncRunning();

        _ = Task.Run(async () =>
        {
            _starting = true;
            try
            {
                await EnsureSignedInAndListeningAsync();
            }
            finally
            {
                _starting = false;
            }
        });
    }

    private async Task EnsureSignedInAndListeningAsync()
    {
        var signIn = await _firebase.SignInAnonymouslyAsync();
        if (!signIn.Success)
        {
            Logger.Warning("VncRelay anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, SignInRetrySeconds);
            var retryTimer = new System.Timers.Timer(SignInRetrySeconds * 1000) { AutoReset = false };
            retryTimer.Elapsed += async (_, _) =>
            {
                retryTimer.Dispose();
                await EnsureSignedInAndListeningAsync();
            };
            retryTimer.Start();
            return;
        }

        _signedIn = true;
        RecreateListener();

        _watchdogTimer?.Dispose();
        _watchdogTimer = new System.Timers.Timer(TimeSpan.FromMinutes(1).TotalMilliseconds) { AutoReset = true };
        _watchdogTimer.Elapsed += (_, _) => CheckListenerHealth();
        _watchdogTimer.Start();
    }

    private void RecreateListener()
    {
        _listener = _firebase.DbListen(
            $"computers/{_computerId}/vncRelay/requested",
            OnSessionRequested);
        _listenerStartedUtc = DateTime.UtcNow;
    }

    // Self-heal a possibly-dead vncRelay/requested listener via two
    // independent checks:
    //  1. LastEventUtc gone stale -> catches a fully frozen stream (no
    //     events of any kind, not even keep-alives).
    //  2. Fixed-age cycling -> catches the "zombie" variant where
    //     keep-alives keep the stream looking alive while real data events
    //     silently stop - see the comment on PeriodicReconnectInterval for
    //     why this can't instead be detected rather than just bounded.
    private void CheckListenerHealth()
    {
        var listener = _listener;
        if (listener == null) return;

        var silentFor = DateTime.UtcNow - listener.LastEventUtc;
        var age = DateTime.UtcNow - _listenerStartedUtc;

        if (silentFor > ListenerStaleThreshold)
        {
            Logger.Warning(
                "vncRelay/requested SSE listener silent for {Minutes:F0} min - forcing restart",
                silentFor.TotalMinutes);
        }
        else if (age > PeriodicReconnectInterval)
        {
            Logger.Information(
                "vncRelay/requested SSE listener reached {Minutes:F0} min - proactive reconnect",
                age.TotalMinutes);
        }
        else
        {
            return;
        }

        Logger.Warning("DIAG CheckListenerHealth: stopping old listener + recreating (activeListenersBefore={ActiveListeners}) at {Utc:O}", SseListener.ActiveCount, DateTime.UtcNow);
        listener.Stop();
        RecreateListener();
        Logger.Warning("DIAG CheckListenerHealth: recreate call returned (activeListenersAfter={ActiveListeners}) at {Utc:O}", SseListener.ActiveCount, DateTime.UtcNow);
    }

    public void Stop()
    {
        _listener?.Stop();
        _activeSessionCts?.Cancel();
    }

    private void EnsureTightVncRunning()
    {
        try
        {
            DisableLegacyTvnServerService();
            EnsureNoAuthRegistry();
            EnsureTightVncDpiCompatibility();

            if (Process.GetProcessesByName("tvnserver").Length > 0) return;

            if (!File.Exists(TightVncExePath))
            {
                Logger.Warning("TightVNC not found at {Path} - has install-tightvnc.ps1 run on this machine yet?", TightVncExePath);
                return;
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = TightVncExePath,
                Arguments = "-run",
                UseShellExecute = false,
                CreateNoWindow = true,
            });
            Logger.Information("Started tvnserver.exe -run in this session (not as a Windows service, so it can see the real kiosk desktop)");
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to launch tvnserver.exe (non-fatal - a VNC session request will fail to connect until this is running)");
        }
    }

    // install-tightvnc.ps1 already disables a pre-existing "tvnserver"
    // Windows service on fresh installs/reinstalls, but that script only
    // runs as an MSI CustomAction - kiosks that only ever received the
    // lightweight file-based auto-update (the normal path) never had a
    // chance to run it. Found live on 13/09/2026: a leftover tvnserver
    // service (from before session-mode was adopted) was still running as
    // NT AUTHORITY\SYSTEM and listening specifically on 127.0.0.1:5900,
    // which Windows always prefers over our session-mode instance's
    // 0.0.0.0:5900 - so VncRelayService's 127.0.0.1 connection silently
    // went to the wrong (Session-0, black-screen) tvnserver every time,
    // with no exception anywhere in this file to explain why. Doing the
    // same cleanup here, on every launch, reaches every already-deployed
    // kiosk without needing a manual fix or a full reinstall.
    private static void DisableLegacyTvnServerService()
    {
        try
        {
            using var sc = new ServiceController("tvnserver");
            if (sc.Status != ServiceControllerStatus.Stopped)
            {
                sc.Stop();
                sc.WaitForStatus(ServiceControllerStatus.Stopped, TimeSpan.FromSeconds(10));
            }

            using var key = Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Services\tvnserver", writable: true);
            key?.SetValue("Start", 4, RegistryValueKind.DWord); // 4 = Disabled
        }
        catch (InvalidOperationException)
        {
            // No such service on this machine - nothing to clean up.
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to disable legacy tvnserver Windows service (non-fatal - if present, it will keep winning the 127.0.0.1:5900 binding)");
        }
    }

    // TightVNC reads its configuration from a completely different registry
    // hive depending on how it runs: as a Windows service it reads HKLM
    // (which is what install-tightvnc.ps1 writes to), but launched directly
    // via "tvnserver.exe -run" - which is what we do here, since a Session-0
    // service can't see the real kiosk desktop - it reads HKEY_CURRENT_USER
    // instead. That meant install-tightvnc.ps1's HKLM write never had any
    // effect on the process this service actually launches: tvnserver kept
    // demanding VNC Authentication with no password configured ("Server is
    // not configured properly"), rejecting every relay connection. Found via
    // manual field debugging on 11/09/2026, confirmed by comparing HKLM
    // (showed UseVncAuthentication=0, had no effect) against HKCU (was
    // completely empty - tvnserver was just running its own hardcoded
    // default of "require auth, no password set").
    //
    // AllowLoopback=1 is a second, unrelated key needed for the same
    // reason: VncRelayService always connects to TightVNC via 127.0.0.1
    // (not the kiosk's LAN IP), and TightVNC refuses loopback RFB
    // connections outright unless this is explicitly enabled - confirmed
    // live via noVNC's exact error "Sorry, loopback connections are not
    // enabled" even after UseVncAuthentication was already fixed.
    //
    // Writing this here, right before every launch, also self-heals kiosks
    // that already have a stale/empty HKCU key from before this fix - the
    // very next time tvnserver isn't already running (next kiosk login or
    // reboot) it will pick up the correct value.
    private static void EnsureNoAuthRegistry()
    {
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(@"SOFTWARE\TightVNC\Server");
            key.SetValue("UseVncAuthentication", 0, RegistryValueKind.DWord);
            key.SetValue("AllowLoopback", 1, RegistryValueKind.DWord);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to set TightVNC no-auth/loopback registry values under HKCU (non-fatal - VNC connections will fail until this is set)");
        }
    }

    // Added 2026-09-14, after community research turned up an exact match
    // for the reported symptom (a click on a small target - AeroAdmin's
    // approval dialog - never registers, while a click anywhere generously
    // sized on the open desktop still roughly works): this is a
    // well-documented TightVNC/UltraVNC bug class on any display running
    // above 100% Windows scaling. tvnserver is an old GDI app with no
    // per-monitor DPI awareness of its own, so Windows silently
    // virtualizes both its screen capture AND the coordinates it injects
    // through SendInput/SetCursorPos into a scaled, non-physical
    // coordinate space - see TightVNC bug #1196 ("makes the TightVNC
    // Server application unusable while DPI is set to 150%") and the
    // matching UltraVNC forum thread, both found via web search. The
    // offset grows the further a click is from the top-left corner, and
    // is proportional to the scaling percentage - which is exactly why a
    // big taskbar icon still basically works but a small dialog button
    // consistently misses.
    //
    // The standard fix (normally set by hand via
    // Properties > Compatibility > "Override high DPI scaling behavior" >
    // System (Enhanced)) is this exact registry value - setting it here
    // means every kiosk self-heals the next time tvnserver isn't already
    // running, with no manual step and no separate installer action.
    //
    // NOTE: if this turns out to be the whole story, the SionyxInputInjector
    // SYSTEM service added earlier the same day may not even be needed for
    // the AeroAdmin case - it only actually helps if a dialog additionally
    // runs at a higher Windows integrity level (still relevant for real
    // UAC/Secure-Desktop prompts). Test this fix first; it's the simpler,
    // fully-automatic one.
    private static void EnsureTightVncDpiCompatibility()
    {
        try
        {
            using var key = Registry.CurrentUser.CreateSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers");
            key.SetValue(TightVncExePath, "~ GDIDPISCALING DPIUNAWARE", RegistryValueKind.String);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Failed to set TightVNC DPI-compatibility registry flag (non-fatal - clicks may be offset on a scaled display until this is set)");
        }
    }

    private void OnSessionRequested(string eventType, JsonElement? data)
    {
        if (eventType != "put" && eventType != "patch") return;
        if (data == null || data.Value.ValueKind != JsonValueKind.Object) return;

        var obj = data.Value;
        var token = obj.TryGetProperty("token", out var t) ? t.GetString() : null;
        var requestedAt = obj.TryGetProperty("requestedAt", out var r) && r.TryGetInt64(out var ra) ? ra : 0;

        if (string.IsNullOrWhiteSpace(token) || requestedAt == 0) return;

        // DIAG (temporary, added 2026-09-23) - logged BEFORE the dedup
        // check/write, on purpose: if two SseListener deliveries ever race
        // each other here, both DIAG lines below should appear with the
        // same requestedAt, close timestamps, and (usually) different
        // thread ids - proving the race independently of whether the dedup
        // check happened to catch it. Cross-reference with the
        // "DIAG SseListener#N delivering" lines to see which listener(s)
        // fired it, and with SseListener.ActiveCount to see if two
        // listeners were alive when it happened.
        Logger.Warning(
            "DIAG OnSessionRequested ENTER token={TokenPrefix}... requestedAt={RequestedAt} lastHandled={LastHandled} activeListeners={ActiveListeners} at {Utc:O} thread={ThreadId}",
            token[..Math.Min(6, token.Length)], requestedAt, _lastHandledRequestedAt, SseListener.ActiveCount, DateTime.UtcNow, Environment.CurrentManagedThreadId);

        if (requestedAt == _lastHandledRequestedAt) return; // SSE replay of the same request
        _lastHandledRequestedAt = requestedAt;

        Logger.Warning("VNC session requested from dashboard (token {Token}...)", token[..Math.Min(6, token.Length)]);
        Logger.Warning(
            "DIAG OnSessionRequested PROCEEDING (won dedup) token={TokenPrefix}... requestedAt={RequestedAt} activeSessionCtsWasNull={WasNull} at {Utc:O} thread={ThreadId}",
            token[..Math.Min(6, token.Length)], requestedAt, _activeSessionCts == null, DateTime.UtcNow, Environment.CurrentManagedThreadId);

        // A new request replaces any session still running.
        _activeSessionCts?.Cancel();
        var cts = new CancellationTokenSource(MaxSessionDuration);
        _activeSessionCts = cts;
        _ = Task.Run(() => RunSessionAsync(token, cts.Token));
    }

    // Exposed so other services can tell "an admin is actually looking at
    // this screen right now via VNC" apart from normal unattended kiosk
    // operation - see AeroAdminSetupService's hide-enforcement, which
    // needs to stop yanking away a real incoming-connection dialog while
    // someone is trying to click it, without giving up on suppressing
    // AeroAdmin's own noise (EULA popups etc.) the rest of the time.
    public static bool IsSessionActive { get; private set; }

    private async Task RunSessionAsync(string token, CancellationToken ct)
    {
        // ServerResolver.GetVncRelayBaseUrl() returns a full scheme+host
        // (e.g. "ws://83.229.22.45:3002" when the local PC is active) or
        // null to keep today's Render/Registry behavior exactly as-is.
        var localBase = ServerResolver.GetVncRelayBaseUrl();
        string relayBaseUrl;
        if (localBase != null)
        {
            relayBaseUrl = localBase;
        }
        else
        {
            var relayHost = RegistryConfig.ReadValue("VncRelayUrl", DefaultRelayHost)!.Trim().TrimEnd('/');
            relayHost = relayHost.Replace("https://", "").Replace("wss://", "").Replace("http://", "");
            relayBaseUrl = $"wss://{relayHost}";
        }
        var relayUri = new Uri($"{relayBaseUrl}/agent/{Uri.EscapeDataString(token)}");

        WebSocket? ws = null;
        using var tcp = new TcpClient();

        EnsureTightVncRunning(); // safety net in case it wasn't running at Start()

        try
        {
            ws = await ConnectRelayWebSocketAsync(relayUri, ct);
            Logger.Information("VNC relay WebSocket connected to {Host}", relayBaseUrl);

            await tcp.ConnectAsync(VncHost, VncPort, ct);
            Logger.Information("Connected to local VNC server on {Host}:{Port}", VncHost, VncPort);

            await ReportResultAsync("connected");
            await ClearRequestedAsync();
            IsSessionActive = true;

            var netStream = tcp.GetStream();
            var wsToTcp = PumpWebSocketToTcpAsync(ws, netStream, ct);
            var tcpToWs = PumpTcpToWebSocketAsync(netStream, ws, ct);
            // Fire-and-forget, deliberately not part of the WhenAny below:
            // this is the "V מוגבר" elevated-click side channel (added
            // 2026-09-14, see SionyxInputInjector/README.md - UNVERIFIED on
            // real hardware). If it fails to connect or errors mid-session
            // that must never end the actual VNC session, which is the
            // part that's already proven to work.
            _ = RunControlChannelAsync(token, relayBaseUrl, ct);
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
            IsSessionActive = false;
            try { if (ws?.State == WebSocketState.Open) await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "done", CancellationToken.None); }
            catch { /* best effort */ }
            ws?.Dispose();
            await ReportResultAsync("ended");
        }
    }

    // Connects to the relay's WebSocket endpoint, trying the standard
    // .NET ClientWebSocket handshake first and falling back to a raw,
    // hand-built HTTP Upgrade request (mimicking PowerShell 5.1's
    // Invoke-WebRequest header shape) if that fails.
    //
    // Added 2026-09-23, after RelayProbe (a standalone diagnostic tool)
    // proved on a real affected kiosk that ClientWebSocket.ConnectAsync
    // gets back HTTP 418 instead of 101 Switching Protocols on networks
    // running NetFree (or a similar TLS-intercepting content filter) -
    // that status code is the filter actively fingerprinting and blocking
    // .NET's default request shape (header order/casing, no manually-set
    // Connection value, ALPN offered, etc.), not the relay server itself
    // rejecting the connection. The exact same request sent with
    // PowerShell-style headers (Connection: Upgrade, Keep-Alive as one
    // value; Host header last; no ALPN) sailed through with a real 101 on
    // the same network - that's the "manual:ps" variant reproduced below.
    // Used for both the main /agent byte-pipe and the /controlAgent
    // elevated-click channel, since both are blocked by the same filter.
    private static async Task<WebSocket> ConnectRelayWebSocketAsync(Uri relayUri, CancellationToken ct)
    {
        try
        {
            var ws = new ClientWebSocket();
            await ws.ConnectAsync(relayUri, ct);
            return ws;
        }
        catch (OperationCanceledException)
        {
            throw; // real cancellation/timeout - never mask this as a handshake problem
        }
        catch (Exception ex)
        {
            Logger.Warning(ex,
                "Standard WebSocket handshake to {Uri} failed (likely NetFree/a filtering proxy fingerprinting .NET's default request shape) - falling back to manual PowerShell-style handshake",
                relayUri);
            return await ConnectViaManualHandshakeAsync(relayUri, ct);
        }
    }

    private static async Task<WebSocket> ConnectViaManualHandshakeAsync(Uri relayUri, CancellationToken ct)
    {
        var host = relayUri.Host;
        var isSecure = relayUri.Scheme == "wss";
        var port = relayUri.Port != -1 ? relayUri.Port : (isSecure ? 443 : 80);

        var tcpClient = new TcpClient();
        await tcpClient.ConnectAsync(host, port, ct);

        Stream stream = tcpClient.GetStream();
        if (isSecure)
        {
            var sslStream = new SslStream(stream, leaveInnerStreamOpen: false);
            // No ALPN - matches PowerShell's default TLS ClientHello shape,
            // which is what got a real 101 through the filtering proxy in
            // RelayProbe. Offering ALPN (as ClientWebSocket does by
            // default) is part of what makes .NET's ClientHello fingerprint
            // differently and get blocked.
            var sslOptions = new SslClientAuthenticationOptions
            {
                TargetHost = host,
                ApplicationProtocols = null,
            };
            await sslStream.AuthenticateAsClientAsync(sslOptions, ct);
            stream = sslStream;
        }

        var key = Convert.ToBase64String(Guid.NewGuid().ToByteArray());

        // Header order/casing deliberately mimics PowerShell 5.1's
        // Invoke-WebRequest shape: Connection is a single comma-joined
        // "Upgrade, Keep-Alive" value, and Host is sent LAST - this exact
        // shape is what RelayProbe's manual:ps variant proved gets a real
        // 101 Switching Protocols through the filtering proxy, unlike
        // ClientWebSocket's default request.
        var sb = new StringBuilder();
        sb.Append("GET ").Append(relayUri.PathAndQuery).Append(" HTTP/1.1\r\n");
        sb.Append("Pragma: no-cache\r\n");
        sb.Append("Upgrade: websocket\r\n");
        sb.Append("Connection: Upgrade, Keep-Alive\r\n");
        sb.Append("Sec-WebSocket-Key: ").Append(key).Append("\r\n");
        sb.Append("Sec-WebSocket-Version: 13\r\n");
        sb.Append("Cache-Control: no-cache\r\n");
        sb.Append("Host: ").Append(host).Append("\r\n\r\n");

        var requestBytes = Encoding.ASCII.GetBytes(sb.ToString());
        await stream.WriteAsync(requestBytes, ct);
        await stream.FlushAsync(ct);

        var statusLine = await ReadHttpResponseHeadersAsync(stream, ct);
        if (!statusLine.Contains(" 101 "))
        {
            throw new WebSocketException(
                $"Manual handshake to {relayUri} failed: server returned '{statusLine.Trim()}' instead of 101 Switching Protocols");
        }

        Logger.Information("Manual handshake succeeded ({StatusLine}) - relay connected via fallback path", statusLine.Trim());

        // Hand the already-upgraded stream to a standard WebSocket object
        // so the rest of this file's pump methods (PumpWebSocketToTcpAsync
        // / PumpTcpToWebSocketAsync) can keep working with it exactly like
        // the ClientWebSocket path - no separate frame-parsing code needed,
        // and no risk of double-buffering bytes that belong to the WS frame
        // stream.
        return WebSocket.CreateFromStream(stream, isServer: false, subProtocol: null, keepAliveInterval: TimeSpan.FromSeconds(30));
    }

    // Reads HTTP response headers byte-by-byte until the blank line that
    // ends them, and returns just the status line. Only ever reads a few
    // hundred bytes at handshake time, so the per-byte overhead here
    // doesn't matter - what does matter is not buffering ahead past the
    // header block, since anything read past it would actually be the
    // start of the raw WebSocket frame stream that WebSocket.CreateFromStream
    // needs to see untouched.
    private static async Task<string> ReadHttpResponseHeadersAsync(Stream stream, CancellationToken ct)
    {
        var lineBuffer = new StringBuilder();
        var singleByte = new byte[1];

        async Task<string> ReadLineAsync()
        {
            lineBuffer.Clear();
            while (true)
            {
                var read = await stream.ReadAsync(singleByte, ct);
                if (read == 0) break; // connection closed mid-handshake
                var c = (char)singleByte[0];
                if (c == '\n') break;
                if (c != '\r') lineBuffer.Append(c);
            }
            return lineBuffer.ToString();
        }

        var statusLine = await ReadLineAsync();
        while (true)
        {
            var line = await ReadLineAsync();
            if (string.IsNullOrEmpty(line)) break; // blank line = end of headers
        }
        return statusLine;
    }

    private static async Task PumpWebSocketToTcpAsync(WebSocket ws, Stream tcp, CancellationToken ct)
    {
        var buffer = new byte[16 * 1024];
        while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            var result = await ws.ReceiveAsync(buffer, ct);
            if (result.MessageType == WebSocketMessageType.Close) break;
            if (result.Count > 0) await tcp.WriteAsync(buffer, 0, result.Count, ct);
        }
    }

    private static async Task PumpTcpToWebSocketAsync(Stream tcp, WebSocket ws, CancellationToken ct)
    {
        var buffer = new byte[16 * 1024];
        while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            var read = await tcp.ReadAsync(buffer, 0, buffer.Length, ct);
            if (read == 0) break; // remote closed the VNC connection
            await ws.SendAsync(new ArraySegment<byte>(buffer, 0, read), WebSocketMessageType.Binary, true, ct);
        }
    }

    // "V מוגבר" (elevated click) side channel - added 2026-09-14.
    // UNVERIFIED end-to-end on real hardware, see
    // src/SionyxInputInjector/README.md before trusting this in the field.
    //
    // Deliberately a completely separate WebSocket from the main
    // /agent/<token> byte-pipe above (not multiplexed onto it): the main
    // pipe forwards raw, unparsed bytes straight into TightVNC's TCP
    // socket, so mixing a JSON control message into that stream would risk
    // corrupting the VNC protocol if anything here misbehaves. Keeping
    // them separate means a bug in this method can, at worst, make the
    // elevated-click button silently do nothing - it can't touch the VNC
    // session that's already proven to work.
    private static async Task RunControlChannelAsync(string token, string relayBaseUrl, CancellationToken ct)
    {
        WebSocket? controlWs = null;
        try
        {
            var controlUri = new Uri($"{relayBaseUrl}/controlAgent/{Uri.EscapeDataString(token)}");
            controlWs = await ConnectRelayWebSocketAsync(controlUri, ct);
            Logger.Information("VNC elevated-click control channel connected");

            var buffer = new byte[4 * 1024];
            while (controlWs.State == WebSocketState.Open && !ct.IsCancellationRequested)
            {
                var result = await controlWs.ReceiveAsync(buffer, ct);
                if (result.MessageType == WebSocketMessageType.Close) break;
                if (result.Count <= 0) continue;

                var json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                await ForwardToInputInjectorAsync(json, ct);
            }
        }
        catch (OperationCanceledException)
        {
            // session ended - normal
        }
        catch (Exception ex)
        {
            // Never let a control-channel problem surface as a session
            // failure - the elevated-click button is a bonus feature, not
            // part of the core VNC session's success/failure reporting.
            Logger.Warning(ex, "VNC elevated-click control channel error (non-fatal - normal VNC session is unaffected)");
        }
        finally
        {
            controlWs?.Dispose();
        }
    }

    // Opens a fresh pipe connection per command rather than keeping one
    // open for the session - elevated clicks are rare (a handful per
    // session at most), so the extra ~few ms of connect overhead per call
    // is a fair trade for not having to detect/recover a stale long-lived
    // pipe connection if SionyxInputInjector restarts mid-session.
    private static async Task ForwardToInputInjectorAsync(string jsonLine, CancellationToken ct)
    {
        try
        {
            // InOut (not Out): SionyxInputInjector now writes a one-line
            // JSON result back per command (see PipeServerWorker), which is
            // what lets this log the REAL outcome instead of just "a line
            // was sent" - see SendCtrlAltDel's own comment for why that
            // distinction matters most for exactly this command.
            using var pipe = new NamedPipeClientStream(".", "SionyxInputInjector", PipeDirection.InOut, PipeOptions.Asynchronous);
            using var connectCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            connectCts.CancelAfter(TimeSpan.FromSeconds(2));
            await pipe.ConnectAsync(connectCts.Token);

            var bytes = Encoding.UTF8.GetBytes(jsonLine.TrimEnd('\n') + "\n");
            await pipe.WriteAsync(bytes, ct);
            await pipe.FlushAsync(ct);

            using var responseCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            responseCts.CancelAfter(TimeSpan.FromSeconds(2));
            using var reader = new StreamReader(pipe, Encoding.UTF8, leaveOpen: true);
            var responseLine = await reader.ReadLineAsync(responseCts.Token);
            if (responseLine != null)
            {
                using var doc = JsonDocument.Parse(responseLine);
                var root = doc.RootElement;
                var type = root.TryGetProperty("type", out var t) ? t.GetString() : "unknown";
                var ok = root.TryGetProperty("ok", out var okEl) && okEl.GetBoolean();
                if (ok)
                {
                    Logger.Information("SionyxInputInjector confirmed {Type} succeeded", type);
                }
                else
                {
                    Logger.Warning("SionyxInputInjector reported {Type} did NOT succeed - see its own logs (Windows Event Log, source SionyxInputInjector) on this kiosk for why", type);
                }
            }
            else
            {
                // Older SionyxInputInjector build (pre-response-protocol) or
                // it closed the pipe before replying - fall back to the old
                // delivery-only confirmation rather than treating this as a
                // failure.
                Logger.Information("Sent to SionyxInputInjector pipe (no result line received): {Command}", jsonLine.TrimEnd('\n'));
            }
        }
        catch (Exception ex)
        {
            // Most likely SionyxInputInjector isn't installed/running yet
            // on this kiosk (this whole feature ships before the service
            // does, see README) - log once per attempt, not fatal to
            // anything.
            Logger.Warning(ex, "Could not reach SionyxInputInjector pipe - is the service installed and running?");
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
