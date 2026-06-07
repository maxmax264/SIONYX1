content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''        private static void RemoveUserAndProfile(string username, Session session)
        {
            string sid = GetUserSid(username);

            // מחק רק את חשבון המשתמש - לא את הפרופיל!
            if (UserExists(username, session))
            {
                RunCommand("net", $"user \\"{username}\\" /delete", session);
                session.Log($"[OK] User account \'{username}\' deleted");
            }

            // מחק רק את רשומת ה-.bak אם קיימת
            if (sid != null)
            {
                string bakRegPath = $@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{sid}.bak";
                try
                {
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    {
                        baseKey.DeleteSubKeyTree(bakRegPath, false);
                        session.Log("[OK] .bak ProfileList entry removed");
                    }
                }
                catch { /* already clean */ }

                // אל תמחק את ProfileList הרגיל ואל תמחק את C:\\Users\\username
                session.Log("[INFO] Profile folder and ProfileList preserved for reinstall");
            }

            string profilePath = $@"C:\\Users\\{username}";
            if (Directory.Exists(profilePath))
            {
                try
                {
                    Directory.Delete(profilePath, true);
                    session.Log($"[OK] Profile folder deleted: {profilePath}");
                }
                catch
                {
                    session.Log($"[WARN] Could not fully delete {profilePath} — may need reboot");
                    RunCommand("cmd", $"/c rmdir /s /q \\"{profilePath}\\"", session);
                }
            }
        }'''

new = '''        private static void RemoveUserAndProfile(string username, Session session)
        {
            session.Log($"=== RemoveUserAndProfile: cleaning everything for {username} ===");
            string sid = GetUserSid(username);

            // 1. Delete user account
            if (UserExists(username, session))
            {
                RunCommand("net", $"user \\"{username}\\" /delete", session);
                session.Log($"[OK] User account \'{username}\' deleted");
            }
            else
            {
                session.Log($"[INFO] User \'{username}\' not found — skipping");
            }

            // 2. Delete ProfileList entries (normal + .bak)
            if (sid != null)
            {
                foreach (var suffix in new[] { "", ".bak" })
                {
                    string regPath = $@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{sid}{suffix}";
                    try
                    {
                        using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                        {
                            baseKey.DeleteSubKeyTree(regPath, false);
                            session.Log($"[OK] ProfileList entry removed: {sid}{suffix}");
                        }
                    }
                    catch { session.Log($"[INFO] ProfileList entry not found: {sid}{suffix}"); }
                }
            }

            // 3. Delete profile folder and all stale SionyxUser.* / TEMP.* folders
            string usersDir = @"C:\\Users";
            foreach (var dir in Directory.GetDirectories(usersDir))
            {
                string name = Path.GetFileName(dir);
                if (name == username || name.StartsWith(username + ".") || name.StartsWith("TEMP."))
                {
                    try
                    {
                        Directory.Delete(dir, true);
                        session.Log($"[OK] Deleted folder: {name}");
                    }
                    catch
                    {
                        RunCommand("cmd", $"/c rmdir /s /q \\"{dir}\\"", session);
                        session.Log($"[OK] Deleted folder via cmd: {name}");
                    }
                }
            }

            // 4. Disable AutoLogon
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", true))
                {
                    if (key != null)
                    {
                        key.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                        try { key.DeleteValue("DefaultPassword", false); } catch { }
                        try { key.DeleteValue("AutoLogonCount", false); } catch { }
                        session.Log("[OK] AutoLogon disabled");
                    }
                }
            }
            catch (Exception ex) { session.Log($"[WARN] AutoLogon cleanup: {ex.Message}"); }

            // 5. Remove FirstLogon scheduled task
            RunCommand("schtasks", "/delete /tn \\"SIONYX_FirstLogon\\" /f", session);
            session.Log("[OK] SIONYX_FirstLogon task removed (if existed)");

            session.Log("=== RemoveUserAndProfile: DONE ===");
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
