content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', encoding='utf-8').read()
old = '      <Custom Action="CA_LaunchKiosk"        After="CA_VerifyInstallation"  Condition="NOT REMOVE" />'
new = '      <Custom Action="CA_LaunchKiosk"        After="CA_VerifyInstallation"  Condition="NOT REMOVE" />\n      <Custom Action="CA_SetupUpdateTask"  After="CA_LaunchKiosk"          Condition="NOT REMOVE" />'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
