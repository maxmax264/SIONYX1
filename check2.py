with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8-sig') as f:
    content = f.read()

old = '''private static void RemoveUserAndProfile(string username, Session session)
        {
            string sid = GetUserSid(username);

            if (UserExists(username, session))
            {
                RunCommand("net", $"user \\"{username}\\" /delete", session);
                session.Log($"[OK] User account \'{username}\' deleted");
            }

            if (sid != null)
            {
                try
                {
                    using (var searcher = new ManagementObjectSearcher(
                        $"SELECT * FROM Win32_UserProfile WHERE SID = \'{sid}\'"))
                    {
                        foreach (ManagementObject profile in searcher.Get())
                        {
                            profile.Delete();
                            session.Log($"[OK] WMI profile removed for SID {sid}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    session.Log($"[WARN] WMI profile removal failed: {ex.Message}");
                }

                string profileRegPath = $@"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{sid}";
                try
                {
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    {
                        baseKey.DeleteSubKeyTree(profileRegPath, false);
                        session.Log("[OK] ProfileList registry entry removed");
                    }
                }
                catch { /* already clean */ }
            }'''

count = content.count(old)
print(f"Found {count} matches")
print(repr(content[33509:33509+100]))
