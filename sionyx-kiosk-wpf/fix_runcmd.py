content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command "" + fullCmd + """, session);\n'
new = '                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command \\"" + fullCmd + "\\"", session);\n'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
