content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                // In immediate mode, read directly from session properties\n                string installDir = session["INSTALLFOLDER"] ?? session.CustomActionData["INSTALLDIR"] ?? @"C:\\Program Files\\SIONYX";'

new = '                string installDir = session.CustomActionData["INSTALLDIR"] ?? @"C:\\Program Files\\SIONYX\\";'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
