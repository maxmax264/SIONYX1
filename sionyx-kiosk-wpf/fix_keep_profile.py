path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = '''            // 3. Delete profile folder and all stale SionyxUser.* / TEMP.* folders
              string usersDir = @"C:\\Users";
              foreach (var dir in Directory.GetDirectories(usersDir))
              {
                  string name = Path.GetFileName(dir);
                  if (name == username || name.StartsWith(username + ".") || name.StartsWith("TEMP."))'''

new = '''            // 3. Delete ONLY stale SionyxUser.* / TEMP.* folders — keep main profile folder
              string usersDir = @"C:\\Users";
              foreach (var dir in Directory.GetDirectories(usersDir))
              {
                  string name = Path.GetFileName(dir);
                  if (name.StartsWith(username + ".") || name.StartsWith("TEMP."))'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
