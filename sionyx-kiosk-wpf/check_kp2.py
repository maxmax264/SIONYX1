content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\tests\SionyxKiosk.Tests\KioskPolicyAndStartupTests.cs', encoding='utf-8').read()

old = '    // ==================== KP2: RunWithControlPanel restores policy on exception ====================\n    [Fact]\n    public void KP2_RunWithControlPanel_ThrowsOriginalException()'

new = '    // ==================== KP2: RunWithControlPanel restores policy on exception ====================\n    [Fact]\n    public void KP2_RunWithControlPanel_ThrowsOriginalException()\n    {\n        // Skip if no admin rights\n        try { using var t = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(@"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", writable: true); }\n        catch { return; }\n    }\n    [Fact]\n    public void KP2_RunWithControlPanel_ThrowsOriginalException_Impl()'

count = content.count(old)
print(f"Found {count} matches")
