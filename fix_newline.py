f = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8')
c = f.read()
f.close()

c = c.replace(
    'PendingRename registered for {mainProfile}\n";',
    'PendingRename registered for {mainProfile}\\n");'
)
c = c.replace(
    'PendingRename FAILED: {rex.Message}\n";',
    'PendingRename FAILED: {rex.Message}\\n");'
)

f = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8')
f.write(c)
f.close()
print("SAVED")
