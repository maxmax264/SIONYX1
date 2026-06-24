content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '<Triggers/>\n  <Actions Context=""Author""><Exec><Command>{appExe}</Command><Arguments>--kiosk</Arguments></Exec></Actions>\n</Task>";'

new = '<Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>\n  <Actions Context=""Author""><Exec><Command>{appExe}</Command><Arguments>--kiosk</Arguments></Exec></Actions>\n</Task>";'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
