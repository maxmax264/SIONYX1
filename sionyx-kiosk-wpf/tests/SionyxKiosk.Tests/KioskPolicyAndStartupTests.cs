using FluentAssertions;
using Microsoft.Win32;
using System.Diagnostics;

namespace SionyxKiosk.Tests;

/// <summary>
/// Tests guarding the kiosk policy and auto-start mechanisms.
/// Safe tests only - do not call Apply/Remove directly (they restart explorer).
/// </summary>
public class KioskPolicyAndStartupTests
{
    private const string PolicyKey = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";

    // ==================== KP1: Registry key path is correct ====================
    [Fact]
    public void KP1_PolicyRegistryKey_IsCorrectPath()
    {
        // Verify the policy key path is the known-correct Windows path
        const string expected = @"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer";
        var field = typeof(SionyxKiosk.Services.KioskPolicyService)
            .GetField("PolicyKey", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
        field.Should().NotBeNull("KioskPolicyService must have PolicyKey constant");
        var actual = field!.GetValue(null) as string;
        actual.Should().Be(expected, "PolicyKey path must match Windows standard path");
    }

    // ==================== KP2: RunWithControlPanel throws original exception ====================
    [Fact]
    public void KP2_RunWithControlPanel_ThrowsOriginalException()
    {
        // Test the logic only - RunWithControlPanel must propagate exceptions
        var act = () => SionyxKiosk.Services.KioskPolicyService.RunWithControlPanel(() =>
            throw new InvalidOperationException("test error"));
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("test error");
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

        // If task doesn't exist on dev machine, skip
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

        // Only check on machines where SIONYX is installed
        if (val == null) return;

        val.Should().Contain("--kiosk", "SIONYX Run key must include --kiosk flag");
        val.Should().Contain("SionyxKiosk.exe", "SIONYX Run key must point to correct exe");
    }
}
