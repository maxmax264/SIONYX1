content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '<Custom Action="CA_VerifyInstallation"'
new = '''<Custom Action="CA_SetupFirstLogon" After="CA_SetupAutoStart" Condition="NOT Installed AND NOT REMOVE" />
        <Custom Action="CA_VerifyInstallation"'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
