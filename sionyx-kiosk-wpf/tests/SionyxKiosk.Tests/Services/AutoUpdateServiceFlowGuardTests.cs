using FluentAssertions;
using System.Reflection;
namespace SionyxKiosk.Tests.Services;
/// <summary>
/// AU9-AU12: Guard tests for the update flow logic, MSI structure, and install safety.
/// </summary>
public class AutoUpdateServiceFlowGuardTests
{
    private static string GetSourceFile()
    {
        var dir = System.IO.Path.GetDirectoryName(
            typeof(SionyxKiosk.Services.AutoUpdateService).Assembly.Location)!
                .Replace(@"\bin\Debug\net8.0-windows", "");
        return System.IO.Path.Combine(dir, "Services", "AutoUpdateService.cs");
    }

    // ==================== AU9: Session check before install ====================
    [Fact]
    public void AU9_CheckAndUpdateAsync_ChecksSessionBeforeInstalling()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("HasActiveSession",
            "Must check SessionStateService.HasActiveSession() before installing");
        content.Should().Contain("DownloadInBackgroundAsync",
            "When session is active, must download in background instead of installing");
        content.Should().Contain("DownloadAndInstallAsync",
            "When no active session, must install immediately");

        // Verify background download comes AFTER session check
        var sessionIdx = content.IndexOf("HasActiveSession");
        var bgIdx = content.IndexOf("DownloadInBackgroundAsync");
        var installIdx = content.IndexOf("DownloadAndInstallAsync");
        sessionIdx.Should().BeLessThan(bgIdx,
            "HasActiveSession check must come before DownloadInBackgroundAsync");
        sessionIdx.Should().BeLessThan(installIdx,
            "HasActiveSession check must come before DownloadAndInstallAsync");
    }

    // ==================== AU10: TryInstallPendingUpdateAsync called after session ends ====================
    [Fact]
    public void AU10_TryInstallPendingUpdateAsync_GuardsWithHasPendingUpdate()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("TryInstallPendingUpdateAsync",
            "Must have TryInstallPendingUpdateAsync for post-session install");
        content.Should().Contain("HasPendingUpdate",
            "TryInstallPendingUpdateAsync must guard with HasPendingUpdate check");
        content.Should().Contain("pending_update.txt",
            "Background download must write pending_update.txt trigger file");
    }

    // ==================== AU11: MSI file naming uses version + ticks (unique) ====================
    [Fact]
    public void AU11_MsiFilename_UsesVersionAndTicks()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("sionyx_update_",
            "MSI filename must start with sionyx_update_");
        content.Should().Contain("DateTime.UtcNow.Ticks",
            "MSI filename must include Ticks to ensure uniqueness across retries");
        content.Should().Contain(".msi",
            "MSI filename must end with .msi extension");
    }

    // ==================== AU12: Cooldown prevents install loop ====================
    [Fact]
    public void AU12_InstallAsync_EnforcesCooldown()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("_lastInstallAttemptUtc",
            "InstallAsync must track last install attempt time");
        content.Should().Contain("InstallCooldown",
            "InstallAsync must enforce cooldown before installing");
        content.Should().Contain("_lastInstallAttemptUtc = DateTime.UtcNow",
            "InstallAsync must update _lastInstallAttemptUtc on each attempt");

        // Cooldown check must come before actual install
        var cooldownIdx = content.IndexOf("sinceLastAttempt < InstallCooldown");
        var taskIdx = content.IndexOf("TryRunViaScheduledTask");
        cooldownIdx.Should().BeLessThan(taskIdx,
            "Cooldown check must happen before TryRunViaScheduledTask");
    }

    // ==================== AU13: Download verifies file size before install ====================
    [Fact]
    public void AU13_Download_VerifiesFileSizeBeforeInstall()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("ContentLength",
            "Must read Content-Length to know expected file size");
        content.Should().Contain("fileInfo.Length",
            "Must verify downloaded file size matches expected size");
        content.Should().Contain("File.Delete",
            "Must delete corrupt file if size mismatch");
    }

    // ==================== AU14: Periodic timer stops before restart ====================
    [Fact]
    public void AU14_PeriodicTimer_StopsBeforeRestart()
    {
        var src = GetSourceFile();
        if (!System.IO.File.Exists(src)) return;
        var content = System.IO.File.ReadAllText(src);

        content.Should().Contain("_periodicTimer?.Stop()",
            "Must stop periodic timer before restarting kiosk to prevent duplicate installs");
        content.Should().Contain("_periodicTimer?.Dispose()",
            "Must dispose periodic timer before restarting kiosk");

        // Stop must come before Process.Start (restart)
        var stopIdx = content.LastIndexOf("_periodicTimer?.Stop()");
        var restartIdx = content.IndexOf("Process.Start");
        stopIdx.Should().BeLessThan(restartIdx,
            "Timer must be stopped before Process.Start restarts the kiosk");
    }
}
