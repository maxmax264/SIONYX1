using System.Diagnostics;
using System.Net.NetworkInformation;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Services;

namespace SionyxInputInjector;

/// <summary>
/// Runs the kiosk's VNC bridge (the same VncRelayService source SionyxKiosk.exe
/// uses) inside this LocalSystem service, so it is available from the moment
/// Windows boots - including after a power outage, while the machine is still
/// sitting at the login screen and SionyxKiosk.exe has not started yet.
///
/// The dashboard flow is unchanged: the button writes
/// computers/{id}/vncRelay/requested in Firebase, this service (anonymous
/// Firebase identity, no user needed) sees it, connects TightVNC to the
/// relay, and the admin's browser (noVNC) shows whatever is on screen -
/// login screen included - and can type the password.
///
/// TightVNC itself runs as a real Windows service (see VncRelayService.
/// EnsureTightVncService): only a service-mode TightVNC follows the active
/// console session and can capture the login screen / Ctrl+Alt+Del / UAC.
///
/// While this service heartbeats (HKLM\SOFTWARE\SIONYX\VncHostHeartbeat), the
/// kiosk app leaves the bridge to it. UNVERIFIED on real hardware - see README.
/// </summary>
internal sealed class VncHostWorker : BackgroundService
{
    private static readonly TimeSpan HeartbeatInterval = TimeSpan.FromSeconds(30);
    private static readonly TimeSpan ConfigRetryInterval = TimeSpan.FromSeconds(30);

    private readonly ILogger<VncHostWorker> _log;

    public VncHostWorker(ILogger<VncHostWorker> log)
    {
        _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // Don't block host startup with the synchronous work below.
        await Task.Yield();

        var relays = new List<VncRelayService>();
        try
        {
            VncRelayService.WriteHostHeartbeat();
            ConfigureServiceRecovery();

            // The computer id is derived from the first network adapter that
            // is "Up" (DeviceInfo) and is computed ONCE per process. Right
            // after a power outage no adapter may be up yet, which would
            // give a different id (a hash of the machine name) than the one
            // the dashboard knows. So wait for a network first.
            if (!await WaitForNetworkAsync(TimeSpan.FromMinutes(5), stoppingToken)) return;

            while (!stoppingToken.IsCancellationRequested && relays.Count == 0)
            {
                try
                {
                    var config = FirebaseConfig.Load();
                    ServerResolver.Start(config); // same failover awareness as the kiosk app

                    // Adapter order can differ between boot time and later
                    // (Bluetooth/VPN adapters), so besides the id the kiosk
                    // app would compute, also listen under the other local
                    // adapters' ids - only one of them is the id the
                    // dashboard actually writes to.
                    var primaryId = DeviceInfo.GetDeviceId();
                    var ids = new List<string> { primaryId };
                    var fallbackId = DeviceInfo.GetFallbackDeviceId();
                    if (!ids.Contains(fallbackId)) ids.Add(fallbackId);
                    foreach (var id in LocalAdapterIds())
                    {
                        if (!ids.Contains(id) && ids.Count < 6) ids.Add(id);
                    }

                    foreach (var id in ids)
                    {
                        var relay = new VncRelayService(config, systemHostMode: true, deviceIdOverride: id);
                        relay.Start();
                        relays.Add(relay);
                    }
                    _log.LogInformation("VNC host started for {Count} computer id(s), primary {PrimaryId} - the dashboard can now reach this machine before login", ids.Count, primaryId);
                    Serilog.Log.Information("VNC host started inside SionyxInputInjector service (ids: {Ids})", string.Join(",", ids));
                }
                catch (Exception ex)
                {
                    foreach (var r in relays) r.Stop();
                    relays.Clear();
                    _log.LogWarning(ex, "VNC host could not start yet (Firebase config missing?) - retrying in {Seconds}s", ConfigRetryInterval.TotalSeconds);
                    Serilog.Log.Warning(ex, "VNC host could not start yet - retrying");
                    if (!await DelayAsync(ConfigRetryInterval, stoppingToken)) return;
                }
            }

            var tick = 0;
            while (!stoppingToken.IsCancellationRequested)
            {
                VncRelayService.WriteHostHeartbeat();
                if (++tick % 2 == 0)
                {
                    // Every ~minute: TightVNC service still installed/running/configured?
                    // (the installer's 15-minute loop only handles "not installed at all")
                    VncRelayService.EnsureHostTightVncService();
                }
                if (!await DelayAsync(HeartbeatInterval, stoppingToken)) break;
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "VNC host worker crashed");
            Serilog.Log.Error(ex, "VNC host worker crashed");
        }
        finally
        {
            foreach (var r in relays) r.Stop();
            VncRelayService.WriteHostHeartbeat(alive: false); // lets the kiosk app take over right away
            Serilog.Log.CloseAndFlush();
        }
    }

    private static bool AnyNetworkUp()
    {
        try
        {
            return NetworkInterface.GetAllNetworkInterfaces().Any(n =>
                n.OperationalStatus == OperationalStatus.Up &&
                n.NetworkInterfaceType != NetworkInterfaceType.Loopback);
        }
        catch
        {
            return false;
        }
    }

    // Returns false only when the service is stopping. After the timeout it
    // proceeds anyway (better a possibly-different id than no bridge at all).
    private async Task<bool> WaitForNetworkAsync(TimeSpan timeout, CancellationToken ct)
    {
        var deadline = DateTime.UtcNow + timeout;
        while (!AnyNetworkUp() && DateTime.UtcNow < deadline)
        {
            if (!await DelayAsync(TimeSpan.FromSeconds(5), ct)) return false;
        }
        _log.LogInformation("Network adapter up: {Up}", AnyNetworkUp());
        return true;
    }

    // Same format as DeviceInfo's MAC-based id: 12 lowercase hex chars.
    private static IEnumerable<string> LocalAdapterIds()
    {
        var result = new List<string>();
        try
        {
            foreach (var nic in NetworkInterface.GetAllNetworkInterfaces())
            {
                if (nic.NetworkInterfaceType is NetworkInterfaceType.Loopback or NetworkInterfaceType.Tunnel) continue;
                var bytes = nic.GetPhysicalAddress().GetAddressBytes();
                if (bytes.Length != 6 || bytes.All(b => b == 0)) continue;
                var id = string.Concat(bytes.Select(b => b.ToString("x2")));
                if (!result.Contains(id)) result.Add(id);
            }
        }
        catch
        {
            // best effort
        }
        return result;
    }

    private static async Task<bool> DelayAsync(TimeSpan delay, CancellationToken ct)
    {
        try
        {
            await Task.Delay(delay, ct);
            return true;
        }
        catch (OperationCanceledException)
        {
            return false;
        }
    }

    // A machine that lost power and came back must end up with this service
    // running: restart it automatically if it ever crashes. Idempotent.
    private void ConfigureServiceRecovery()
    {
        try
        {
            using var p = Process.Start(new ProcessStartInfo
            {
                FileName = "sc.exe",
                Arguments = "failure SionyxInputInjector reset= 86400 actions= restart/5000/restart/5000/restart/60000",
                UseShellExecute = false,
                CreateNoWindow = true,
            });
            p?.WaitForExit(10000);
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Could not configure service recovery actions (non-fatal)");
        }
    }
}
