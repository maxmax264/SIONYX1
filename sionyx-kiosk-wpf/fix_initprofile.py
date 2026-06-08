content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                if (Directory.Exists(profilePath))\n                {\n                    Directory.Delete(profilePath, true);\n                    session.Log($"[OK] Deleted old profile folder: {profilePath}");\n                    File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\\n");\n                }'

new = '                if (Directory.Exists(profilePath))\n                {\n                    try\n                    {\n                        Directory.Delete(profilePath, true);\n                        session.Log($"[OK] Deleted old profile folder: {profilePath}");\n                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\\n");\n                    }\n                    catch (Exception ex)\n                    {\n                        session.Log($"[WARN] Could not delete profile folder (locked): {ex.Message} - continuing");\n                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] WARNING: could not delete profile folder\\n");\n                    }\n                }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
