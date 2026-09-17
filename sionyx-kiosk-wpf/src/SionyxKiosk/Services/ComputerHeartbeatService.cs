using Serilog;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Infrastructure.Logging;

namespace SionyxKiosk.Services;

public class ComputerHeartbeatService
{
    private static readonly ILogger Logger = Log.ForContext<ComputerHeartbeatService>();
    private const int IntervalSeconds = 60;
    private const int SignInRetrySeconds = 30;

    private readonly FirebaseClient _deviceFirebase;
    private readonly string _computerId;
    private System.Timers.Timer? _timer;
    private bool _starting;
    private bool _signedIn;

    public ComputerHeartbeatService(FirebaseConfig config)
    {
        _deviceFirebase = new FirebaseClient(config);
        _computerId = DeviceInfo.GetDeviceId();
    }

    /// <summary>
    /// Starts reporting "alive" heartbeats to the dashboard, independent of any
    /// logged-in user (called once from the auth/login screen at app startup).
    ///
    /// Bug fixed: this used to give up permanently if the one-off anonymous
    /// Firebase sign-in failed on its very first attempt - e.g. a transient
    /// network hiccup right at boot, or a NetFree-style filter that hasn't
    /// finished warming up yet. Since Start() is only called once (from
    /// StartGlobalHotkey, guarded so it can't run twice), that single failure
    /// meant NO heartbeat for the rest of the session - which looked exactly
    /// like "no signal until a user logs in", because by the time a user logs
    /// in the network/filter has usually settled and other Firebase calls
    /// (that DO retry per-call) start working. Now sign-in retries on a timer
    /// until it succeeds, instead of failing silently once and never trying again.
    /// </summary>
    public void Start()
    {
        if (_timer != null || _starting || _signedIn) return;

        _ = Task.Run(async () =>
        {
            _starting = true;
            try
            {
                await EnsureSignedInAndReportingAsync();
            }
            finally
            {
                _starting = false;
            }
        });
    }

    private async Task EnsureSignedInAndReportingAsync()
    {
        var signIn = await _deviceFirebase.SignInAnonymouslyAsync();
        if (!signIn.Success)
        {
            Logger.Warning("Heartbeat anonymous sign-in failed: {Error} - retrying in {Seconds}s", signIn.Error, SignInRetrySeconds);
            var retryTimer = new System.Timers.Timer(SignInRetrySeconds * 1000) { AutoReset = false };
            retryTimer.Elapsed += async (_, _) =>
            {
                retryTimer.Dispose();
                await EnsureSignedInAndReportingAsync();
            };
            retryTimer.Start();
            return;
        }

        _signedIn = true;
        await SendHeartbeatAsync();

        _timer = new System.Timers.Timer(IntervalSeconds * 1000);
        _timer.Elapsed += async (_, _) => await SendHeartbeatAsync();
        _timer.AutoReset = true;
        _timer.Start();
    }

    // Added 2026-09-15: read-only check, NEVER reads or reports the
    // DefaultPassword value - only whether AutoAdminLogon is turned on and
    // a username is set. Motivation: a kiosk without Windows auto-logon
    // configured sits at the Windows password screen after any restart
    // (dashboard-triggered via RemoteCommandService, a power outage,
    // anything) - and at that screen, SionyxKiosk.exe (and therefore
    // VncRelayService/TightVNC, all of it) hasn't even started yet, so
    // remote support can't see or reach the machine at all. This makes
    // that state visible on the dashboard proactively instead of only
    // being discovered the hard way after an actual restart.
    private static (bool configured, string? user) CheckAutoLogon()
    {
        try
        {
            using var key = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon");
            var autoAdminLogon = key?.GetValue("AutoAdminLogon") as string;
            var defaultUser = key?.GetValue("DefaultUserName") as string;
            var configured = autoAdminLogon == "1" && !string.IsNullOrEmpty(defaultUser);
            return (configured, defaultUser);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Could not check AutoAdminLogon registry state (non-fatal)");
            return (false, null);
        }
    }

    private async Task SendHeartbeatAsync()
    {
        try
        {
            var (autoLogonConfigured, autoLogonUser) = CheckAutoLogon();
            if (!autoLogonConfigured)
            {
                Logger.Warning("Windows AutoAdminLogon is NOT configured on this kiosk - a restart will stop at the Windows logon screen, where remote support (VNC, etc.) cannot reach it at all until someone logs in physically");
            }

            // install-tightvnc.ps1 downloads TightVNC's installer live from
            // tightvnc.com during setup (Return="ignore" on that CustomAction
            // means an MSI install can "succeed" overall even if this one
            // download failed - e.g. Netfree not yet whitelisting that
            // domain on a freshly-deployed machine/network). Without this
            // check, that failure is invisible until someone tries VNC and
            // it hangs on "connecting" forever with no obvious cause.
            var tightVncInstalled = System.IO.File.Exists(@"C:\Program Files\TightVNC\tvnserver.exe");
            if (!tightVncInstalled)
            {
                Logger.Warning("TightVNC is NOT installed on this kiosk (C:\\Program Files\\TightVNC\\tvnserver.exe missing) - remote VNC support will hang on 'connecting' forever. Likely cause: the live download in install-tightvnc.ps1 failed, often because Netfree hasn't whitelisted tightvnc.com on this machine/network yet");
            }
            ChannelLogSink.Current?.ReportStatus("tightvnc", tightVncInstalled,
                tightVncInstalled ? null : "tvnserver.exe missing - install-tightvnc.ps1 download likely failed");

            // SionyxInputInjector: the SYSTEM service behind Ctrl+Alt+Del,
            // elevated-click, and the AeroAdmin-approval workaround. Checked
            // the same way as tightVncInstalled above - if the MSI's
            // CustomAction ever silently skips installing it (e.g. the
            // publish step failed at build time, see build.ps1's
            // Invoke-PublishInputInjector), this makes that visible on the
            // dashboard instead of only discovered by a dead Ctrl+Alt+Del
            // button with no error anywhere.
            bool inputInjectorRunning;
            try
            {
                using var sc = new System.ServiceProcess.ServiceController("SionyxInputInjector");
                inputInjectorRunning = sc.Status == System.ServiceProcess.ServiceControllerStatus.Running;
            }
            catch
            {
                inputInjectorRunning = false; // service doesn't exist at all
            }
            if (!inputInjectorRunning)
            {
                Logger.Warning("SionyxInputInjector service is NOT running on this kiosk - Ctrl+Alt+Del and elevated-click via VNC will silently do nothing. Likely cause: the MSI's publish step for this project failed at build time, or the service crashed");
            }
            ChannelLogSink.Current?.ReportStatus("inputInjector", inputInjectorRunning,
                inputInjectorRunning ? null : "SionyxInputInjector service missing or not running");

            var result = await _deviceFirebase.DbUpdateAsync($"computers/{_computerId}",
                new Dictionary<string, object>
                {
                    ["heartbeatAt"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                    // Reported every beat (not just at registration) so the dashboard
                    // always shows the version currently running, even if the name
                    // or version was set/changed after this machine was first set up.
                    ["appVersion"] = DeviceInfo.GetAppVersion(),
                    ["autoLogonConfigured"] = autoLogonConfigured,
                    ["autoLogonUser"] = autoLogonUser ?? "",
                    ["tightVncInstalled"] = tightVncInstalled,
                    ["inputInjectorRunning"] = inputInjectorRunning,
                });
            if (!result.Success)
                Logger.Warning("Heartbeat write failed: {Error}", result.Error);

            await SyncComputerNameAsync();
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Heartbeat write threw (non-fatal)");
        }
    }

    /// <summary>
    /// Raised when the dashboard-side computer name changes, so any open UI
    /// (e.g. the login screen watermark) can refresh itself without a restart.
    /// </summary>
    public static event Action<string>? ComputerNameUpdated;

    /// <summary>Local (HKCU) cache of the name the dashboard currently shows.</summary>
    public const string DashboardNameValue = "DashboardComputerName";

    /// <summary>
    /// Keeps the install-time name and the dashboard name in sync, in the one
    /// direction each that the user actually wants:
    ///
    ///  - Firebase has NO name yet (fresh install, nobody has logged in on this
    ///    machine): seed it from the install-time registry name, so the name
    ///    typed during setup shows up in the dashboard on its own, within one
    ///    heartbeat, without waiting for a user login. This was the actual bug -
    ///    computerName was only ever written by ComputerService.RegisterComputerAsync(),
    ///    which only runs on login, so an installed-but-not-yet-used kiosk showed
    ///    "ללא שם" in the dashboard even though the kiosk itself displayed the name.
    ///
    ///  - Firebase HAS a name: the dashboard wins (that's where renames happen,
    ///    e.g. when machines are physically moved around), and we mirror it into
    ///    HKCU so the kiosk's own screens show the same name. We deliberately do
    ///    NOT push the registry name over it, which would make the dashboard's
    ///    rename button silently revert every 60s.
    /// </summary>
    private async Task SyncComputerNameAsync()
    {
        try
        {
            var read = await _deviceFirebase.DbGetAsync($"computers/{_computerId}/computerName");
            if (!read.Success) return;

            var dbName = read.Data is System.Text.Json.JsonElement el
                         && el.ValueKind == System.Text.Json.JsonValueKind.String
                ? el.GetString()
                : null;

            if (string.IsNullOrWhiteSpace(dbName))
            {
                var installName = RegistryConfig.ReadValue("ComputerName");
                if (string.IsNullOrWhiteSpace(installName))
                    installName = DeviceInfo.GetComputerName();
                if (string.IsNullOrWhiteSpace(installName)) return;

                var seed = await _deviceFirebase.DbUpdateAsync($"computers/{_computerId}",
                    new Dictionary<string, object> { ["computerName"] = installName });
                if (seed.Success)
                    Logger.Information("Seeded dashboard computer name from install-time registry value: {Name}", installName);
                return;
            }

            var cached = RegistryConfig.ReadValueCurrentUser(DashboardNameValue);
            if (cached == dbName) return;

            RegistryConfig.WriteValue(DashboardNameValue, dbName!);
            Logger.Information("Computer name updated from dashboard: {Name}", dbName);
            ComputerNameUpdated?.Invoke(dbName!);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "Computer name sync failed (non-fatal)");
        }
    }

    public void Stop()
    {
        _timer?.Stop();
        _timer?.Dispose();
        _timer = null;
        _signedIn = false;
    }
}