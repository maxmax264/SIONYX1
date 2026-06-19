content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', encoding='utf-8').read()
old = '    <CustomAction Id="CA_LaunchKiosk"        BinaryRef="CustomActionsDll" DllEntry="LaunchKiosk"        Execute="deferred" Impersonate="yes" Return="ignore" />'
new = '    <CustomAction Id="CA_LaunchKiosk"        BinaryRef="CustomActionsDll" DllEntry="LaunchKiosk"        Execute="deferred" Impersonate="yes" Return="ignore" />\n    <CustomAction Id="CA_SetupUpdateTask"  BinaryRef="CustomActionsDll" DllEntry="SetupUpdateTask"  Execute="deferred" Impersonate="no"  Return="ignore" />'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
