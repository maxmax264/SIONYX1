using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.ServiceProcess;
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
    private const string DefaultRelayHost = "sionyx-vnc-relay.onrender.com";
    private const string VncHost = "127.0.0.1";
    private const int VncPort = 5900;
    private const string TightVncExePath = @"C:\Program Files\TightVNC\tvnserver.exe";
    private static readonly TimeSpan MaxSessionDuration = TimeSpan.FromMinutes(30);
    private const int SignInRetrySeconds = 30;

    private readonly FirebaseClient _firebase;
    private string? _computerId;
    private SseListener? _listener;
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
        _listener = _firebase.DbListen(
            $"computers/{_computerId}/vncRelay/requested",
            OnSessionRequested);
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

            if (Process.GetProcessesByName("tvnserver").Length > 0) return;

            if (!File.Exists(TightVncExePath))
            {
                // install-tightvnc.ps1 runs as an MSI CustomAction during
                // SIONYX's own install - but Windows Installer holds a
                // global mutex for the whole duration of that install, so
                // a nested msiexec (installing TightVNC) fails outright
                // with 1618 ("another installation is already in
                // progress"). The script never checked msiexec's exit
                // code, so this failed completely silently: no warning
                // anywhere, tvnserver-info.txt still got written, and the
                // kiosk was left with the HKCU/HKLM registry values set
                // but no tvnserver.exe to ever use them. Confirmed live
                // on 13/09/2026 (manually re-running the same msiexec
                // command outside the MSI context succeeded immediately).
                // Self-heal here instead: this method runs at every app
                // startup and every VNC request, long after SIONYX's own
                // MSI install has fully finished and released its mutex,
                // so a nested install here does not hit the same problem.
                Logger.Warning("TightVNC not found at {Path} - attempting to install it now (self-heal for a CustomAction that may have failed during setup)", TightVncExePath);
                _ = Task.Run(() => TryInstallTightVncAsync());
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

    private const string TightVncMsiUrl = "https://www.tightvnc.com/download/2.8.88/tightvnc-2.8.88-gpl-setup-64bit.msi";

    // Same install flow/arguments as install-tightvnc.ps1, run here (outside
    // any MSI CustomAction context) so it isn't blocked by SIONYX's own
    // installer mutex. See EnsureTightVncRunning's comment for why this
    // exists. Safe to call repeatedly - if tvnserver.exe already exists by
    // the time this runs, it does nothing.
    private async Task TryInstallTightVncAsync()
    {
        try
        {
            if (File.Exists(TightVncExePath)) return;

            var tempDir = @"C:\Temp";
            Directory.CreateDirectory(tempDir);
            var msiPath = Path.Combine(tempDir, "tightvnc-setup.msi");

            if (!File.Exists(msiPath))
            {
                Logger.Information("Downloading TightVNC installer...");
                using var http = new HttpClient();
                using var response = await http.GetAsync(TightVncMsiUrl);
                response.EnsureSuccessStatusCode();
                await using var fs = File.Create(msiPath);
                await response.Content.CopyToAsync(fs);
            }

            Logger.Information("Installing TightVNC (server only, loopback-only, no VNC auth, not as a Windows service)...");
            var psi = new ProcessStartInfo
            {
                FileName = "msiexec.exe",
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            psi.ArgumentList.Add("/i");
            psi.ArgumentList.Add(msiPath);
            psi.ArgumentList.Add("/quiet");
            psi.ArgumentList.Add("/norestart");
            psi.ArgumentList.Add("ADDLOCAL=Server");
            psi.ArgumentList.Add("SERVER_REGISTER_AS_SERVICE=0");
            psi.ArgumentList.Add("SERVER_ADD_FIREWALL_EXCEPTION=0");
            psi.ArgumentList.Add("SERVER_ALLOW_SAS=1");
            psi.ArgumentList.Add("SET_USEVNCAUTHENTICATION=1");
            psi.ArgumentList.Add("VALUE_OF_USEVNCAUTHENTICATION=0");

            using var proc = Process.Start(psi)!;
            await proc.WaitForExitAsync();

            if (proc.ExitCode != 0)
            {
                Logger.Warning("TightVNC self-heal install failed with msiexec exit code {ExitCode}", proc.ExitCode);
                return;
            }

            if (!File.Exists(TightVncExePath))
            {
                Logger.Warning("msiexec reported success but {Path} still does not exist", TightVncExePath);
                return;
            }

            Logger.Information("TightVNC self-heal install succeeded");
            EnsureTightVncRunning(); // now that the exe exists, start it
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "TightVNC self-heal install failed (non-fatal - a VNC session request will fail to connect until this is resolved)");
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

        EnsureTightVncRunning(); // safety net in case it wasn't running at Start()

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
