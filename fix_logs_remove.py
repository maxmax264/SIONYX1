content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''            session.Log($"=== RemoveUserAndProfile: cleaning everything for {username} ===");
            string sid = GetUserSid(username);'''

new = '''            session.Log($"=== RemoveUserAndProfile: cleaning everything for {username} ===");
            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] === UNINSTALL START for {username} ===\\n");
            string sid = GetUserSid(username);
            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] SID={sid}\\n");'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)

old2 = '''            session.Log("=== RemoveUserAndProfile: DONE ===");'''
new2 = '''            session.Log("=== RemoveUserAndProfile: DONE ===");
            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] === UNINSTALL DONE ===\\n");
            // Check what remains
            bool folderExists = System.IO.Directory.Exists($@"C:\\Users\\{username}");
            bool userExists = false;
            try { new System.Security.Principal.NTAccount(username).Translate(typeof(System.Security.Principal.SecurityIdentifier)); userExists = true; } catch { }
            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] After cleanup — folder exists: {folderExists}, user exists: {userExists}\\n");'''

count2 = content.count(old2)
print(f"Found {count2} matches for DONE")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
