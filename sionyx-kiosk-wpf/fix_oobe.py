content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '''                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                        "DisableTaskMgr", 1);'''
new = '''                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                        "DisableTaskMgr", 1);

                    // Skip Windows OOBE ("Getting Windows ready") on first logon
                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE",
                        "SkipUserOOBE", 1);
                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE",
                        "SkipMachineOOBE", 1);'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
