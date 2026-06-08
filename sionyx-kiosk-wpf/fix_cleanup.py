content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '            RunCommand("schtasks", "/delete /tn \\"SIONYX_FirstLogon\\" /f", session);'

new = r'''            // 4. Clean AutoLogon registry entries
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                {
                    if (key != null)
                    {
                        key.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                        try { key.DeleteValue("DefaultPassword", false); } catch { }
                        try { key.DeleteValue("DefaultUserName", false); } catch { }
                        try { key.DeleteValue("AutoLogonSID", false); } catch { }
                        try { key.DeleteValue("AutoLogonCount", false); } catch { }
                        try { key.DeleteValue("EnableFirstLogonAnimation", false); } catch { }
                        session.Log("[OK] AutoLogon cleaned");
                    }
                }
            }
            catch (Exception ex) { session.Log($"[WARN] AutoLogon cleanup: {ex.Message}"); }

            // 5. Clean SpecialAccounts
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList", true))
                {
                    if (key != null)
                    {
                        try { key.DeleteValue(username, false); } catch { }
                        session.Log("[OK] SpecialAccounts cleaned");
                    }
                }
            }
            catch (Exception ex) { session.Log($"[WARN] SpecialAccounts cleanup: {ex.Message}"); }

            // 6. Remove scheduled tasks
            RunCommand("schtasks", "/delete /tn \"SIONYX_FirstLogon\" /f", session);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND - searching...')
    idx = content.find('RunCommand("schtasks"')
    print(repr(content[idx:idx+80]))
