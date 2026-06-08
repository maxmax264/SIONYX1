content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''                // Delete old profile folder before CreateProfile so it uses the correct path
                if (Directory.Exists(profilePath))
                {
                    try
                    {
                        int rmResult = RunCommand("cmd", $"/c rmdir /s /q \\"{profilePath}\\"", session);'''

new = '''                // Delete old profile folder before CreateProfile so it uses the correct path
                if (Directory.Exists(profilePath))
                {
                    // Unload SionyxUser registry hive before deleting (prevents UsrClass.dat lock)
                    try
                    {
                        string sidForUnload = GetUserSid(KioskUsername);
                        if (sidForUnload != null)
                        {
                            int unloadResult = RunCommand("reg", $"unload \\"HKU\\\\{sidForUnload}\\"", session);
                            session.Log($"[INFO] reg unload result: {unloadResult}");
                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] reg unload result={unloadResult}\\n");
                            System.Threading.Thread.Sleep(500);
                        }
                    }
                    catch (Exception ex)
                    {
                        session.Log($"[WARN] reg unload failed: {ex.Message}");
                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] reg unload failed: {ex.Message}\\n");
                    }
                    try
                    {
                        int rmResult = RunCommand("cmd", $"/c rmdir /s /q \\"{profilePath}\\"", session);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
