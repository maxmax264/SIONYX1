content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '''                session.Log($"[OK] Kiosk user account ready ({sw.ElapsedMilliseconds}ms)");
                return ActionResult.Success;'''
new = '''                // Skip OOBE for all new profiles on this machine
                try
                {
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var oobeKey = baseKey.CreateSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\FirstLogonCommands", true))
                    {
                        // No commands needed - just ensure key exists
                    }
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var oobeKey = baseKey.CreateSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE", true))
                    {
                        oobeKey.SetValue("SkipMachineOOBE", 1, RegistryValueKind.DWord);
                        oobeKey.SetValue("SkipUserOOBE", 1, RegistryValueKind.DWord);
                        session.Log("[OK] OOBE skip flags set in HKLM");
                    }
                }
                catch (Exception ex) { session.Log($"[WARN] OOBE skip: {ex.Message}"); }

                session.Log($"[OK] Kiosk user account ready ({sw.ElapsedMilliseconds}ms)");
                return ActionResult.Success;'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
