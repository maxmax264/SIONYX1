using System.Diagnostics;
using System.IO;
using System.Net.Http;
using Microsoft.Extensions.Logging;

namespace SionyxInputInjector;

/// <summary>
/// Keeps TightVNC installed on this kiosk, retrying periodically rather
/// than giving up after one attempt.
///
/// Why this lives here (a SYSTEM service) rather than in SionyxKiosk.exe
/// itself or purely in install-tightvnc.ps1:
/// - install-tightvnc.ps1 only ever runs once per MSI install/update (a
///   short-lived process with a few retries and then it's done for that
///   version) - if the network/Netfree situation resolves itself later,
///   nothing on the kiosk would notice or retry until the next app update.
/// - SionyxKiosk.exe runs at Medium integrity (the interactive user), so
///   it cannot silently run an elevated msiexec install itself - that's
///   exactly the UIPI problem this whole project already worked around
///   for input injection. This service already runs as LocalSystem for
///   that same reason, so it can just install software directly too.
///
/// Field motivation (2026-09-15): a brand-new kiosk's install failed
/// because Netfree didn't recognize the download's file type at the time.
/// Even after fixing the URL, some future kiosk could hit a similar
/// transient block - this makes recovery automatic instead of needing
/// another full app update to try again.
/// </summary>
internal sealed class TightVncInstaller
{
    public const string ExePath = @"C:\Program Files\TightVNC\tvnserver.exe";

    // Same URL as install-tightvnc.ps1 - kept in sync manually since this
    // is a small, rarely-changed constant, not worth a shared-config file
    // between a C# service and a PowerShell script for one string.
    private const string MsiUrl = "https://github.com/maxmax264/sionyx-releases/releases/download/tightvnc-2.8.88/tightvnc-2.8.88-gpl-setup-64bit.msi";
    private const string MsiArgs = "/i \"{0}\" /quiet /norestart ADDLOCAL=Server SERVER_REGISTER_AS_SERVICE=0 " +
        "SERVER_ADD_FIREWALL_EXCEPTION=0 SERVER_ALLOW_SAS=1 SET_USEVNCAUTHENTICATION=1 VALUE_OF_USEVNCAUTHENTICATION=0";

    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(60) };

    private readonly ILogger<TightVncInstaller> _log;

    public TightVncInstaller(ILogger<TightVncInstaller> log)
    {
        _log = log;
    }

    /// <summary>
    /// Checks once and, if missing, makes one install attempt. Caller is
    /// expected to call this periodically (see PipeServerWorker) rather
    /// than looping internally - "don't give up quickly" means keep
    /// trying across a long period, not hammer the network in a tight
    /// retry loop right now.
    /// </summary>
    public async Task EnsureInstalledAsync(CancellationToken ct)
    {
        if (File.Exists(ExePath))
        {
            return; // already installed - nothing to do, checked cheaply every cycle
        }

        _log.LogWarning("TightVNC not found at {Path} - attempting install (this will keep retrying periodically until it succeeds)", ExePath);

        string? tempMsiPath = null;
        try
        {
            tempMsiPath = Path.Combine(Path.GetTempPath(), "tightvnc-setup.msi");

            await using (var response = await Http.GetStreamAsync(MsiUrl, ct))
            await using (var file = File.Create(tempMsiPath))
            {
                await response.CopyToAsync(file, ct);
            }

            var psi = new ProcessStartInfo
            {
                FileName = "msiexec.exe",
                Arguments = string.Format(MsiArgs, tempMsiPath),
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            using var process = Process.Start(psi);
            if (process == null)
            {
                _log.LogError("Failed to start msiexec.exe for TightVNC install");
                return;
            }
            await process.WaitForExitAsync(ct);

            if (File.Exists(ExePath))
            {
                _log.LogInformation("TightVNC installed successfully (msiexec exit code {Code})", process.ExitCode);
            }
            else
            {
                _log.LogError("msiexec ran (exit code {Code}) but TightVNC still isn't at {Path} - will retry next cycle", process.ExitCode, ExePath);
            }
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "TightVNC install attempt failed (will retry next cycle) - if this keeps failing, check whether {Url} is reachable from this kiosk's network (Netfree)", MsiUrl);
        }
        finally
        {
            if (tempMsiPath != null)
            {
                try { File.Delete(tempMsiPath); } catch { /* best effort cleanup */ }
            }
        }
    }
}
