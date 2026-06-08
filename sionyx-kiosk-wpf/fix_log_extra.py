path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()
log = 'File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log"'

# לוג אחרי יצירת תיקיות
old = 'session.Log("[OK] Profile directories created");'
new = 'session.Log("[OK] Profile directories created");\n                ' + log + ', $"[{DateTime.Now}] Profile dirs created\\n");'

count = content.count(old)
print(f"dirs Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)

# לוג בסוף SetupFirstLogon
old2 = 'session.Log("[OK] AutoLogon configured for SionyxUser (1 time)");'
new2 = 'session.Log("[OK] AutoLogon configured for SionyxUser (1 time)");\n                    ' + log + ', $"[{DateTime.Now}] AutoLogon configured\\n");'

count2 = content.count(old2)
print(f"autologon Found: {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)

open(path, 'w', encoding='utf-8').write(content)
print("OK")
