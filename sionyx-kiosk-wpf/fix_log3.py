content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = 'session.Log($"[DBG] ntuser.dat path: C:\\Users\\{KioskUsername}\\ntuser.dat");\n            session.Log($"[DBG] ntuser.dat exists: {File.Exists($@"C:\\Users\\{KioskUsername}\\ntuser.dat")}");\n            session.Log($"[DBG] Profile dir exists: {Directory.Exists($@"C:\\Users\\{KioskUsername}")}");\n'
new = 'session.Log("[DBG] ntuser.dat path: " + @"C:\Users\" + KioskUsername);\n            session.Log("[DBG] ntuser.dat exists: " + File.Exists(@"C:\Users\" + KioskUsername + @"\ntuser.dat").ToString());\n            session.Log("[DBG] Profile dir exists: " + Directory.Exists(@"C:\Users\" + KioskUsername).ToString());\n'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
