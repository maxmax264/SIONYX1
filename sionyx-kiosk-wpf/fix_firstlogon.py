import re

content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

new_action = '''
        /// <summary>
        /// Sets up AutoLogon for SionyxUser once, so Windows creates a full profile on first boot.
        /// A first-logon script disables AutoLogon after the profile is created.
        /// </summary>
        [CustomAction]
        public static ActionResult SetupFirstLogon(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== SetupFirstLogon: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];

                // Write a PowerShell script that runs on first logon and disables AutoLogon
                string scriptContent = @"
# Disable AutoLogon after first logon
reg delete ""HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"" /v AutoAdminLogon /f 2>$null
reg delete ""HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"" /v DefaultPassword /f 2>$null
reg delete ""HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"" /v AutoLogonCount /f 2>$null
# Remove this script from startup
schtasks /delete /tn ""SIONYX_FirstLogon"" /f 2>$null
";
                string scriptPath = System.IO.Path.Combine(installDir, "first_logon.ps1");
                File.WriteAllText(scriptPath, scriptContent);
                session.Log("[OK] First logon script written to: " + scriptPath);

                // Create scheduled task to run script on first logon of SionyxUser
                string psCmd = "$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-ExecutionPolicy Bypass -WindowStyle Hidden -File """ + scriptPath + @"""'; " +
                    "$trigger = New-ScheduledTaskTrigger -AtLogOn -User 'SionyxUser'; " +
                    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries; " +
                    "$principal = New-ScheduledTaskPrincipal -UserId 'SionyxUser' -LogonType Interactive -RunLevel Highest; " +
                    "Register-ScheduledTask -TaskName 'SIONYX_FirstLogon' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force";

                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command \"" + psCmd + "\"", session);
                session.Log("[OK] First logon task created, exit=" + rc);

                // Enable AutoLogon for SionyxUser (one time)
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                {
                    key.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                    key.SetValue("DefaultUserName", "SionyxUser", RegistryValueKind.String);
                    key.SetValue("DefaultPassword", "", RegistryValueKind.String);
                    key.SetValue("AutoLogonCount", 1, RegistryValueKind.DWord);
                    session.Log("[OK] AutoLogon configured for SionyxUser (1 time)");
                }

                session.Log("=== SetupFirstLogon: DONE (" + sw.ElapsedMilliseconds + "ms) ===");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log("[ERROR] SetupFirstLogon failed: " + ex.Message);
                return ActionResult.Failure;
            }
        }
'''

# Insert before the UNINSTALL ACTIONS comment
old = '        // ====================================================================\n        //  UNINSTALL ACTIONS'
new = new_action + '\n        // ====================================================================\n        //  UNINSTALL ACTIONS'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
