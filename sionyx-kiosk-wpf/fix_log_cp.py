path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

log = 'File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log"'

old = 'int cpResult = CreateProfile(userSid, KioskUsername, profilePathBuilder, (uint)profilePathBuilder.Capacity);\n                    session.Log($"[INFO] CreateProfile API result: {cpResult} path: {profilePathBuilder}");'
new = 'int cpResult = CreateProfile(userSid, KioskUsername, profilePathBuilder, (uint)profilePathBuilder.Capacity);\n                    session.Log($"[INFO] CreateProfile API result: {cpResult} path: {profilePathBuilder}");\n                    ' + log + ', $"[{DateTime.Now}] CreateProfile result={cpResult} path={profilePathBuilder}\\n");'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
