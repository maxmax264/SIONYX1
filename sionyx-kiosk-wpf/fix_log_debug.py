path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = 'session.Log("=== InitializeProfile: START ===");'
new = 'session.Log("=== InitializeProfile: START ===");\n                File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] InitializeProfile: START\\n");'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
