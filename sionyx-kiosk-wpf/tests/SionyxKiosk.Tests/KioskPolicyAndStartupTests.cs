using FluentAssertions;
using Microsoft.Win32;
using System.Diagnostics;
using System.Reflection;
namespace SionyxKiosk.Tests;
public class KioskPolicyAndStartupTests
{
    private const string PolicyKey = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";
    // ==================== KP1: Registry key path is correct ====================
    [Fact]
    public void KP1_PolicyRegistryKey_IsCorrectPath()
    {
        const string expected = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";
        var field = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetField("PolicyKey", BindingFlags.NonPublic | BindingFlags.Static);
        field.Should().NotBeNull("KioskPolicyService must have PolicyKey constant");
        var actual = field!.GetValue(null) as string;
        actual.Should().Be(expected, "PolicyKey path must match Windows standard path");
    }
    // ==================== KP2: RunWithControlPanel throws original exception ====================
    [Fact]
    public void KP2_RunWithControlPanel_ThrowsOriginalException()
    {
        var act = () => SionyxKiosk.Services.KioskPolicyService.RunWithControlPanel(() =>
            throw new InvalidOperationException("test error"));
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("test error");
    }
    // ==================== KP3: RunWithControlPanelAsync exists and is async Task ====================
    [Fact]
    public void KP3_RunWithControlPanelAsync_ExistsAndReturnsTask()
    {
        var method = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetMethod("RunWithControlPanelAsync", BindingFlags.Public | BindingFlags.Static);
        method.Should().NotBeNull("RunWithControlPanelAsync must exist as a public static method");
        method!.ReturnType.Should().Be(typeof(System.Threading.Tasks.Task),
            "RunWithControlPanelAsync must return Task (not void or Task<T>)");
    }
    // ==================== KP4: RunWithControlPanelAsync takes no parameters ====================
    [Fact]
    public void KP4_RunWithControlPanelAsync_TakesNoParameters()
    {
        var method = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetMethod("RunWithControlPanelAsync", BindingFlags.Public | BindingFlags.Static);
        method.Should().NotBeNull();
        method!.GetParameters().Should().BeEmpty(
            "RunWithControlPanelAsync must take no parameters — control panel launch is internal");
    }
    // ==================== KP5: Apply and Remove both exist as public static void ====================
    [Fact]
    public void KP5_ApplyAndRemove_ExistAsPublicStaticVoid()
    {
        var apply = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetMethod("Apply", BindingFlags.Public | BindingFlags.Static);
        var remove = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetMethod("Remove", BindingFlags.Public | BindingFlags.Static);
        apply.Should().NotBeNull("Apply() must exist");
        remove.Should().NotBeNull("Remove() must exist");
        apply!.ReturnType.Should().Be(typeof(void), "Apply must return void");
        remove!.ReturnType.Should().Be(typeof(void), "Remove must return void");
    }
    // ==================== KP6: OpenControlPanelRequested handler uses RunWithControlPanelAsync ====================
    [Fact]
    public void KP6_AppXamlCs_OpenControlPanelHandler_UsesRunWithControlPanelAsync()
    {
        var appXamlPath = System.IO.Path.Combine(
            System.IO.Path.GetDirectoryName(typeof(SionyxKiosk.Services.KioskPolicyService).Assembly.Location)!
                .Replace(@"\bin\Debug\net8.0-windows", ""),
            "App.xaml.cs");
        if (!System.IO.File.Exists(appXamlPath)) return;
        var content = System.IO.File.ReadAllText(appXamlPath);
        content.Should().Contain("RunWithControlPanelAsync()",
            "OpenControlPanelRequested handler must call RunWithControlPanelAsync() with no arguments");
        content.Should().NotContain("RunWithControlPanel(() =>",
            "OpenControlPanelRequested must not use the old synchronous RunWithControlPanel");
    }
    // ==================== KS1: SIONYX_LaunchOnce task has LogonTrigger ====================
    [Fact]
    public void KS1_LaunchOnceTask_HasLogonTrigger()
    {
        var psi = new ProcessStartInfo("schtasks", "/query /tn \"SIONYX_LaunchOnce\" /fo LIST /v")
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            CreateNoWindow = true
        };
        using var proc = Process.Start(psi);
        var output = proc?.StandardOutput.ReadToEnd() ?? "";
        proc?.WaitForExit(5000);
        if (!output.Contains("SIONYX_LaunchOnce")) return;
        output.Should().NotContain("On demand only",
            "SIONYX_LaunchOnce must not be On-demand-only — it needs a LogonTrigger");
    }
    // ==================== KS2: SIONYX Run key exists in HKLM ====================
    [Fact]
    public void KS2_HKLMRunKey_ContainsSionyxWithKioskFlag()
    {
        using var key = Registry.LocalMachine.OpenSubKey(
            @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run");
        var val = key?.GetValue("SIONYX") as string;
        if (val == null) return;
        val.Should().Contain("--kiosk", "SIONYX Run key must include --kiosk flag");
        val.Should().Contain("SionyxKiosk.exe", "SIONYX Run key must point to correct exe");
    }
}
