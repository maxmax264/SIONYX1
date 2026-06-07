content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '<CustomAction Id="CA_VerifyInstallation"'
new = '''<CustomAction Id="CA_SetupFirstLogon" BinaryRef="CustomActionsDll" DllEntry="SetupFirstLogon" Execute="deferred" Impersonate="no" Return="check" />
    <SetProperty Id="CA_SetupFirstLogon" Before="CA_SetupFirstLogon" Sequence="execute" Value="INSTALLDIR=[INSTALLFOLDER]" />
    <CustomAction Id="CA_VerifyInstallation"'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
