path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = '                // Create the profile via Win32 API so Windows does not show "Getting Windows ready"\n                var profilePathBuilder = new StringBuilder(260);\n                string userSid = GetUserSid(KioskUsername);'
new = '                // Delete old profile folder before CreateProfile so it uses the correct path\n                if (Directory.Exists(profilePath))\n                {\n                    Directory.Delete(profilePath, true);\n                    session.Log($"[OK] Deleted old profile folder: {profilePath}");\n                    File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\\n");\n                }\n\n                // Create the profile via Win32 API so Windows does not show "Getting Windows ready"\n                var profilePathBuilder = new StringBuilder(260);\n                string userSid = GetUserSid(KioskUsername);'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
