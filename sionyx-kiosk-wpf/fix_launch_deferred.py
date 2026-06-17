content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '    <CustomAction Id="CA_LaunchKiosk"        BinaryRef="CustomActionsDll" DllEntry="LaunchKiosk"        Execute="immediate" Return="ignore" />'

new = '    <SetProperty Id="CA_LaunchKiosk" Before="CA_LaunchKiosk" Sequence="execute" Value="INSTALLDIR=[INSTALLFOLDER]" />\n    <CustomAction Id="CA_LaunchKiosk"        BinaryRef="CustomActionsDll" DllEntry="LaunchKiosk"        Execute="deferred" Impersonate="yes" Return="ignore" />'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
