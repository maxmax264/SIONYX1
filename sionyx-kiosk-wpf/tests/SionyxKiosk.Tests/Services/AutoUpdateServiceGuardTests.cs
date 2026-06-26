using FluentAssertions;
using System.Reflection;
namespace SionyxKiosk.Tests.Services;
/// <summary>
/// Guard tests for AutoUpdateService — protect the auto-update mechanism from regressions.
/// Safe: no HTTP calls, no registry writes, no file system side-effects.
/// </summary>
public class AutoUpdateServiceGuardTests
{
    private static MethodInfo GetPrivate(string name, int paramCount = 0)
    {
        var methods = typeof(SionyxKiosk.Services.AutoUpdateService)
            .GetMethods(BindingFlags.NonPublic | BindingFlags.Static)
            .Where(m => m.Name == name && m.GetParameters().Length == paramCount)
            .ToList();
        methods.Should().NotBeEmpty($"private method '{name}' must exist in AutoUpdateService");
        return methods.First();
    }
    private static T GetConst<T>(string name)
    {
        var field = typeof(SionyxKiosk.Services.AutoUpdateService)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static);
        field.Should().NotBeNull($"field '{name}' must exist in AutoUpdateService");
        return (T)field!.GetValue(null)!;
    }

    // ==================== AU1: UpdateServerUrl points to correct host ====================
    [Fact]
    public void AU1_UpdateServerUrl_PointsToCorrectHost()
    {
        var url = GetConst<string>("UpdateServerUrl");
        url.Should().Contain("sionyx-auth-server.onrender.com",
            "UpdateServerUrl must point to the SIONYX update server");
        url.Should().Contain("latest-version",
            "UpdateServerUrl must include the /latest-version endpoint");
    }

    // ==================== AU2: InstallCooldown is exactly 2 minutes ====================
    [Fact]
    public void AU2_InstallCooldown_IsTwoMinutes()
    {
        var cooldown = GetConst<TimeSpan>("InstallCooldown");
        cooldown.Should().Be(TimeSpan.FromMinutes(2),
            "InstallCooldown must be 2 minutes to prevent install loops");
    }

    // ==================== AU3: IsNewerVersion — basic cases ====================
    [Theory]
    [InlineData("3.5.0", "3.4.258", true)]
    [InlineData("3.4.259", "3.4.258", true)]
    [InlineData("3.4.258", "3.4.258", false)]
    [InlineData("3.4.257", "3.4.258", false)]
    [InlineData("4.0.0", "3.9.999", true)]
    public void AU3_IsNewerVersion_ReturnsCorrectResult(string latest, string current, bool expected)
    {
        var method = GetPrivate("IsNewerVersion", 2);
        var result = (bool)method.Invoke(null, [latest, current])!;
        result.Should().Be(expected,
            $"IsNewerVersion({latest}, {current}) should be {expected}");
    }

    // ==================== AU4: GetUpdateFolder returns correct path ====================
    [Fact]
    public void AU4_GetUpdateFolder_ReturnsCorrectPath()
    {
        var method = GetPrivate("GetUpdateFolder", 0);
        var result = (string)method.Invoke(null, [])!;
        result.Should().Contain(@"C:\Users\Public\Documents\SIONYX",
            "Update folder must be under Public Documents for correct ACL");
        result.Should().Contain("updates",
            "Update folder must be the 'updates' subfolder");
    }

    // ==================== AU5: TryRunViaScheduledTask uses correct task name ====================
    [Fact]
    public void AU5_ScheduledTaskName_IsCorrect()
    {
        // Verify the scheduled task name is hardcoded correctly in the source
        var sourceFile = System.IO.Path.Combine(
            System.IO.Path.GetDirectoryName(
                typeof(SionyxKiosk.Services.AutoUpdateService).Assembly.Location)!
                    .Replace(@"\bin\Debug\net8.0-windows", ""),
            "Services", "AutoUpdateService.cs");
        if (!System.IO.File.Exists(sourceFile)) return;
        var content = System.IO.File.ReadAllText(sourceFile);
        content.Should().Contain("SIONYX_Update",
            "Scheduled task name must be SIONYX_Update");
        content.Should().NotContain("SIONYX_update",
            "Scheduled task name is case-sensitive — must be SIONYX_Update not SIONYX_update");
    }

    // ==================== AU6: GetInstalledVersion reads correct registry path ====================
    [Fact]
    public void AU6_GetInstalledVersion_ReadsCorrectRegistryPath()
    {
        var sourceFile = System.IO.Path.Combine(
            System.IO.Path.GetDirectoryName(
                typeof(SionyxKiosk.Services.AutoUpdateService).Assembly.Location)!
                    .Replace(@"\bin\Debug\net8.0-windows", ""),
            "Services", "AutoUpdateService.cs");
        if (!System.IO.File.Exists(sourceFile)) return;
        var content = System.IO.File.ReadAllText(sourceFile);
        content.Should().Contain(@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            "GetInstalledVersion must read from the standard Uninstall registry path");
        content.Should().Contain("WOW6432Node",
            "GetInstalledVersion must also check WOW6432Node for 32-bit installs");
        content.Should().Contain("DisplayName",
            "GetInstalledVersion must match on DisplayName");
        content.Should().Contain("DisplayVersion",
            "GetInstalledVersion must read DisplayVersion");
    }

    // ==================== AU7: Public API surface is intact ====================
    [Fact]
    public void AU7_PublicApiSurface_IsIntact()
    {
        var type = typeof(SionyxKiosk.Services.AutoUpdateService);
        type.GetMethod("CheckAndUpdateAsync", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("CheckAndUpdateAsync must exist");
        type.GetMethod("TryInstallPendingUpdateAsync", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("TryInstallPendingUpdateAsync must exist");
        type.GetMethod("ForceUpdateNowAsync", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("ForceUpdateNowAsync must exist");
        type.GetMethod("ApplyIntervalFromRegistry", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("ApplyIntervalFromRegistry must exist");
        type.GetProperty("HasPendingUpdate", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("HasPendingUpdate property must exist");
        type.GetProperty("PendingUpdateVersion", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("PendingUpdateVersion property must exist");
    }

    // ==================== AU8: Progress events exist ====================
    [Fact]
    public void AU8_ProgressEvents_Exist()
    {
        var type = typeof(SionyxKiosk.Services.AutoUpdateService);
        type.GetEvent("UpdateStarted", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("UpdateStarted event must exist");
        type.GetEvent("ProgressChanged", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("ProgressChanged event must exist");
        type.GetEvent("UpdateCompleted", BindingFlags.Public | BindingFlags.Static)
            .Should().NotBeNull("UpdateCompleted event must exist");
    }
}
