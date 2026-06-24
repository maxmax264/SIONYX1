content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                session.Log($"=== SetupAutoStart: DONE ({sw.ElapsedMilliseconds}ms) ===");\n                return ActionResult.Success;'

new = '''                // Configure Auto-login for kiosk user
                try
                {
                    string currentUser = Environment.UserName;
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var winlogon = baseKey.OpenSubKey(@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", true))
                    {
                        if (winlogon != null)
                        {
                            winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                            winlogon.SetValue("DefaultUserName", currentUser, RegistryValueKind.String);
                            winlogon.SetValue("DefaultPassword", "", RegistryValueKind.String);
                            session.Log($"[OK] Auto-login configured for user: {currentUser}");
                        }
                    }
                }
                catch (Exception ex) { session.Log($"[WARN] Auto-login setup failed: {ex.Message}"); }

                session.Log($"=== SetupAutoStart: DONE ({sw.ElapsedMilliseconds}ms) ===");
                return ActionResult.Success;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('SetupAutoStart: DONE')
    print(repr(content[idx:idx+200]))
