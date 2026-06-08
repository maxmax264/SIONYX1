import re

content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '            // 3. Delete ONLY stale SionyxUser.* / TEMP.* folders - keep main profile'

new = r'''            // 3. Delete main profile folder + stale SionyxUser.* / TEMP.* folders
            string mainProfile = System.IO.Path.Combine(@"C:\Users", username);
            if (Directory.Exists(mainProfile))
            {
                try
                {
                    Directory.Delete(mainProfile, true);
                    session.Log($"[OK] Deleted main profile folder: {mainProfile}");
                }
                catch (Exception ex)
                {
                    session.Log($"[WARN] Could not delete {mainProfile} (locked): {ex.Message}");
                    try
                    {
                        using (var regKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                            .OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Session Manager", true))
                        {
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\??\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                        }
                    }
                    catch (Exception rex) { session.Log($"[WARN] PendingRename failed: {rex.Message}"); }
                }
            }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
