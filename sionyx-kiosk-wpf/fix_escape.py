content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = 'RunCommand("schtasks", $"/create /tn "SIONYX_Update" /xml "{xmlPath}" /f", session);'
new = 'RunCommand("schtasks", $"/create /tn \\"SIONYX_Update\\" /xml \\"{xmlPath}\\" /f", session);'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
