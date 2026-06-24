content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', encoding='utf-8').read()

old = '''    private static void SetStartupForUser(string username, bool enabled)
    {
        try
        {
            // Save preference
            using var prefKey = Registry.LocalMachine.CreateSubKey(SionyxStartupKey, writable: true);
            prefKey?.SetValue(username, enabled ? 1 : 0, RegistryValueKind.DWord);

            // Apply to HKCU of current user if it matches
            if (username == Environment.UserName)
            {
                string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location
                    .Replace(".dll", ".exe");
                using var runKey = Registry.CurrentUser.OpenSubKey(RunKey, true);
                if (enabled)
                    runKey?.SetValue(RunValueName, $"\\"{exePath}\\" --kiosk", RegistryValueKind.String);
                else
                    runKey?.DeleteValue(RunValueName, false);
            }
        }
        catch { }
    }'''

new = '''    private static void SetStartupForUser(string username, bool enabled)
    {
        try
        {
            // Save preference
            using var prefKey = Registry.LocalMachine.CreateSubKey(SionyxStartupKey, writable: true);
            prefKey?.SetValue(username, enabled ? 1 : 0, RegistryValueKind.DWord);

            // Configure AutoAdminLogon in Winlogon
            using (var baseKey = Microsoft.Win32.RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, Microsoft.Win32.RegistryView.Registry64))
            using (var winlogon = baseKey.OpenSubKey(@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", true))
            {
                if (winlogon != null)
                {
                    if (enabled)
                    {
                        winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                        winlogon.SetValue("DefaultUserName", username, RegistryValueKind.String);
                        winlogon.DeleteValue("DefaultPassword", false);
                    }
                    else
                    {
                        winlogon.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                    }
                }
            }

            // Apply Run key to HKLM so it works for any user
            string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location
                .Replace(".dll", ".exe");
            using var runKey = Registry.LocalMachine.OpenSubKey(RunKey, true);
            if (enabled)
                runKey?.SetValue(RunValueName, $"\\"{exePath}\\" --kiosk", RegistryValueKind.String);
            else
                runKey?.DeleteValue(RunValueName, false);
        }
        catch { }
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
