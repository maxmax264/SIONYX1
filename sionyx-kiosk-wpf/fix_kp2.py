content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\tests\SionyxKiosk.Tests\KioskPolicyAndStartupTests.cs', encoding='utf-8').read()

old = '''    // ==================== KP2: RunWithControlPanel restores policy on exception ====================
    [Fact]
    public void KP2_RunWithControlPanel_ThrowsOriginalException()
    {
        // Write registry directly without restarting explorer
        using var key = Registry.CurrentUser.CreateSubKey(PolicyKey, writable: true);
        key?.SetValue("NoControlPanel", 1, RegistryValueKind.DWord);

        try
        {
            var act = () => SionyxKiosk.Services.KioskPolicyService.RunWithControlPanel(() =>
                throw new InvalidOperationException("test error"));
            act.Should().Throw<InvalidOperationException>()
                .WithMessage("test error");
        }
        finally
        {
            // Clean up directly without restarting explorer
            using var cleanKey = Registry.CurrentUser.OpenSubKey(PolicyKey, writable: true);
            cleanKey?.DeleteValue("NoControlPanel", false);
        }
    }'''

new = '''    // ==================== KP2: RunWithControlPanel throws original exception ====================
    [Fact]
    public void KP2_RunWithControlPanel_ThrowsOriginalException()
    {
        // Test the logic only - RunWithControlPanel must propagate exceptions
        var act = () => SionyxKiosk.Services.KioskPolicyService.RunWithControlPanel(() =>
            throw new InvalidOperationException("test error"));
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("test error");
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\tests\SionyxKiosk.Tests\KioskPolicyAndStartupTests.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
