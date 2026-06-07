content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                bool exists = UserExists(KioskUsername, session);'

new = r'''                // Clean up stale profile folders (SionyxUser.* and TEMP.*)
                string usersDir = @"C:\Users";
                foreach (var dir in System.IO.Directory.GetDirectories(usersDir))
                {
                    string name = System.IO.Path.GetFileName(dir);
                    if (name.StartsWith(KioskUsername + ".") || name.StartsWith("TEMP."))
                    {
                        try
                        {
                            System.IO.Directory.Delete(dir, true);
                            session.Log($"[OK] Removed stale profile folder: {name}");
                        }
                        catch (Exception ex)
                        {
                            session.Log($"[WARN] Could not remove {name}: {ex.Message}");
                        }
                    }
                }

                bool exists = UserExists(KioskUsername, session);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
