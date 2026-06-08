content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                        Directory.Delete(profilePath, true);\n                        session.Log($"[OK] Deleted old profile folder: {profilePath}");\n                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\\n");\n                    }\n                    catch (Exception ex)\n                    {\n                        session.Log($"[WARN] Could not delete profile folder (locked): {ex.Message} - continuing");\n                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] WARNING: could not delete profile folder\\n");\n                    }'

new = '                        int rmResult = RunCommand("cmd", $"/c rmdir /s /q \\"{profilePath}\\"", session);\n                        if (rmResult == 0)\n                        {\n                            session.Log($"[OK] Deleted old profile folder: {profilePath}");\n                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\\n");\n                        }\n                        else\n                        {\n                            session.Log($"[WARN] rmdir returned {rmResult} - continuing anyway");\n                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] WARNING: rmdir failed, continuing\\n");\n                        }\n                    }\n                    catch (Exception ex)\n                    {\n                        session.Log($"[WARN] Could not delete profile folder: {ex.Message} - continuing");\n                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] WARNING: could not delete profile folder\\n");\n                    }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
