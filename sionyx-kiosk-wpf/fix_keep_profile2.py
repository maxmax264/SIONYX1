path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = 'Delete profile folder and all stale SionyxUser.* / TEMP.* folders\n            string usersDir = @"C:\\Users";\n            foreach (var dir in Directory.GetDirectories(usersDir))\n            {\n                string name = Path.GetFileName(dir);\n                if (name == username || name.StartsWith('

new = 'Delete ONLY stale SionyxUser.* / TEMP.* folders - keep main profile\n            string usersDir = @"C:\\Users";\n            foreach (var dir in Directory.GetDirectories(usersDir))\n            {\n                string name = Path.GetFileName(dir);\n                if (name.StartsWith('

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
