content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '''            session.Log("=== ApplySecurityRestrictions: START ===");'''
new = '''            session.Log("=== ApplySecurityRestrictions: START ===");
            session.Log($"[DBG] ntuser.dat path: C:\\Users\\{KioskUsername}\\ntuser.dat");
            session.Log($"[DBG] ntuser.dat exists: {File.Exists($@"C:\\Users\\{KioskUsername}\\ntuser.dat")}");
            session.Log($"[DBG] Profile dir exists: {Directory.Exists($@"C:\\Users\\{KioskUsername}")}");'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
