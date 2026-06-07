content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''                string psCmd = "$action = New-ScheduledTaskAction -Execute \'powershell.exe\' -Argument \'-ExecutionPolicy Bypass -WindowStyle Hidden -File """ + scriptPath + @"""\'; " +\n                    "$trigger = New-ScheduledTaskTrigger -AtLogOn -User \'SionyxUser\'; " +\n                    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries; " +\n                    "$principal = New-ScheduledTaskPrincipal -UserId \'SionyxUser\' -LogonType Interactive -RunLevel Highest; " +\n                    "Register-ScheduledTask -TaskName \'SIONYX_FirstLogon\' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force";\n\n                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command "" + psCmd + """, session);'''

new = '''                string psCmd = "-ExecutionPolicy Bypass -WindowStyle Hidden -File \\"" + scriptPath + "\\"";
                string fullCmd = "$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '" + psCmd + "'; " +
                    "$trigger = New-ScheduledTaskTrigger -AtLogOn -User 'SionyxUser'; " +
                    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries; " +
                    "$principal = New-ScheduledTaskPrincipal -UserId 'SionyxUser' -LogonType Interactive -RunLevel Highest; " +
                    "Register-ScheduledTask -TaskName 'SIONYX_FirstLogon' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force";

                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command \"" + fullCmd + "\"", session);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
