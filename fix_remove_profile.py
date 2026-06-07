content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '''        private static void RemoveUserAndProfile(string username, Session session)
        {
            string sid = GetUserSid(username);
            if (UserExists(username, session))
            {
                RunCommand("net", $"user \"{username}\" /delete", session);
                session.Log($"[OK] User account '{username}' deleted");
            }
            if (sid != null)
            {
                try
                {
                    using (var searcher = new ManagementObjectSearcher(
                        $"SELECT * FROM Win32_UserProfile WHERE SID = '{sid}'"))
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
                string profileRegPath = $@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{sid}";
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
new = '''        private static void RemoveUserAndProfile(string username, Session session)
        {
            string sid = GetUserSid(username);
            // מחק רק את חשבון המשתמש - לא את הפרופיל!
            if (UserExists(username, session))
            {
                RunCommand("net", $"user \"{username}\" /delete", session);
                session.Log($"[OK] User account \'{username}\' deleted");
            }
            // מחק רק את רשומת ה-.bak אם קיימת
            if (sid != null)
            {
                string bakRegPath = $@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{sid}.bak";
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
            }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
