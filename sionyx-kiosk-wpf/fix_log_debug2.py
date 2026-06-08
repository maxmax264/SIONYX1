path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = 'session.Log("=== SetupFirstLogon: START ===");'
new = 'session.Log("=== SetupFirstLogon: START ===");\n                File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] SetupFirstLogon: START\\n");'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
