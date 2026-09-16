using System.IO.Pipes;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace SionyxInputInjector;

/// <summary>
/// Local IPC endpoint for VncRelayService (running as the interactive user,
/// not SYSTEM) to ask this SYSTEM service to inject a click. Named pipe
/// rather than a loopback TCP port so nothing on the machine's network
/// stack (even 127.0.0.1) needs to change, and so it's naturally
/// unreachable from anywhere off-box.
///
/// Protocol: newline-delimited JSON, one object per line, e.g.
///   {"type":"click","xFrac":0.42,"yFrac":0.61}
/// No response is written back - this is fire-and-forget, matching how the
/// relay's control channel already treats it (see vnc.html). Anything
/// malformed is logged and ignored; a bad line never crashes the pipe.
///
/// UNTESTED - see NativeMethods.cs.
/// </summary>
internal sealed class PipeServerWorker : BackgroundService
{
    public const string PipeName = "SionyxInputInjector";

    private readonly InputInjector _injector;
    private readonly TightVncInstaller _tightVncInstaller;
    private readonly ILogger<PipeServerWorker> _log;

    public PipeServerWorker(InputInjector injector, TightVncInstaller tightVncInstaller, ILogger<PipeServerWorker> log)
    {
        _injector = injector;
        _tightVncInstaller = tightVncInstaller;
        _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var sasChanged = _injector.EnsureSoftwareSasPolicy();
        var uacChanged = _injector.EnsureUacPromptOnNormalDesktop();
        _injector.ScheduleRebootIfPolicyChanged(sasChanged, uacChanged);

        // Fire-and-forget, deliberately not awaited here: "don't give up
        // quickly" means this keeps checking/retrying for as long as the
        // service runs, completely independent of whether the pipe below
        // ever gets a connection. A failure in here must never take down
        // the pipe server (the elevated-click/Ctrl+Alt+Del feature), so it
        // has its own try/catch per cycle inside RunTightVncMaintenanceLoopAsync.
        _ = RunTightVncMaintenanceLoopAsync(stoppingToken);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var pipe = CreatePipe();
                _log.LogInformation("Waiting for a connection on pipe {PipeName}", PipeName);
                await pipe.WaitForConnectionAsync(stoppingToken);
                await HandleClientAsync(pipe, stoppingToken);
            }
            catch (OperationCanceledException)
            {
                // shutting down
            }
            catch (Exception ex)
            {
                // Never let one bad connection kill the loop - a kiosk that
                // needs this working when it's needed can't afford the
                // whole service exiting over a single malformed client.
                _log.LogError(ex, "Pipe server loop error - restarting listener");
                await Task.Delay(1000, stoppingToken).ContinueWith(_ => { });
            }
        }
    }

    // "Don't give up quickly" - checks every 15 minutes for as long as the
    // service runs, forever, rather than only during install/update. A
    // Netfree block that clears up later (or gets whitelisted by an admin
    // after noticing the tightVncInstalled=false heartbeat) gets picked up
    // automatically on the very next cycle, no further app update needed.
    private static readonly TimeSpan TightVncCheckInterval = TimeSpan.FromMinutes(15);

    private async Task RunTightVncMaintenanceLoopAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await _tightVncInstaller.EnsureInstalledAsync(stoppingToken);
            }
            catch (OperationCanceledException)
            {
                // shutting down
            }
            catch (Exception ex)
            {
                _log.LogError(ex, "TightVNC maintenance cycle threw unexpectedly - will retry next cycle regardless");
            }

            try { await Task.Delay(TightVncCheckInterval, stoppingToken); }
            catch (OperationCanceledException) { /* shutting down */ }
        }
    }

    private static NamedPipeServerStream CreatePipe()
    {
        // Grant connect access to the local interactive user (the account
        // SionyxKiosk/VncRelayService actually runs as) in addition to the
        // defaults (which only cover the pipe's creator, SYSTEM, and
        // Administrators) - without this, a normal-user client gets
        // UnauthorizedAccessException connecting to a pipe SYSTEM created.
        var security = new PipeSecurity();
        security.AddAccessRule(new PipeAccessRule(
            new SecurityIdentifier(WellKnownSidType.BuiltinUsersSid, null),
            PipeAccessRights.ReadWrite,
            AccessControlType.Allow));
        security.AddAccessRule(new PipeAccessRule(
            new SecurityIdentifier(WellKnownSidType.LocalSystemSid, null),
            PipeAccessRights.FullControl,
            AccessControlType.Allow));

        return NamedPipeServerStreamAcl.Create(
            PipeName,
            PipeDirection.In,
            1,
            PipeTransmissionMode.Byte,
            PipeOptions.Asynchronous,
            inBufferSize: 4096,
            outBufferSize: 0,
            pipeSecurity: security);
    }

    private async Task HandleClientAsync(NamedPipeServerStream pipe, CancellationToken ct)
    {
        using var reader = new StreamReader(pipe, Encoding.UTF8, leaveOpen: true);
        string? line;
        while ((line = await reader.ReadLineAsync(ct)) != null)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            try
            {
                using var doc = JsonDocument.Parse(line);
                var root = doc.RootElement;
                var type = root.TryGetProperty("type", out var t) ? t.GetString() : null;
                if (type == "click"
                    && root.TryGetProperty("xFrac", out var xEl)
                    && root.TryGetProperty("yFrac", out var yEl))
                {
                    _injector.TryClick(xEl.GetDouble(), yEl.GetDouble());
                }
                else if (type == "ctrlaltdel")
                {
                    _injector.SendCtrlAltDel();
                }
                else if (type == "typeText" && root.TryGetProperty("text", out var textEl))
                {
                    _injector.TryTypeText(textEl.GetString() ?? string.Empty);
                }
                else
                {
                    _log.LogWarning("Ignoring unrecognized command: {Line}", line);
                }
            }
            catch (JsonException ex)
            {
                _log.LogWarning(ex, "Ignoring malformed line: {Line}", line);
            }
        }
    }
}
