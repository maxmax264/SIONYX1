content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', encoding='utf-8').read()

old = '    private static bool IsStartupEnabledForUser(string username)'

new = '''    private static void SetAutoLogin(string username)
    {
        try
        {
            using var baseKey = Microsoft.Win32.RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, Microsoft.Win32.RegistryView.Registry64);
            using var winlogon = baseKey.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true);
            using var runKey = baseKey.OpenSubKey(RunKey, true);
            if (winlogon == null) return;

            string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location.Replace(".dll", ".exe");

            if (!string.IsNullOrEmpty(username))
            {
                winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                winlogon.SetValue("DefaultUserName", username, RegistryValueKind.String);
                winlogon.DeleteValue("DefaultPassword", false);
                runKey?.SetValue(RunValueName, $"\\"{exePath}\\" --kiosk", RegistryValueKind.String);
            }
            else
            {
                winlogon.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                runKey?.DeleteValue(RunValueName, false);
            }
        }
        catch { }
    }

    private static bool IsStartupEnabledForUser(string username)'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
