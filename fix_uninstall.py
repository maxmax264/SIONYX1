content = open(
    r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs',
    encoding='utf-8'
).read()

# ================================================================
# תיקון 1: unload hive + rmdir לפני Directory.Delete
# ================================================================
old1 = """            // 3. Delete main profile folder + stale SionyxUser.* / TEMP.* folders
            string mainProfile = System.IO.Path.Combine(@"C:\\Users", username);
            if (Directory.Exists(mainProfile))
            {
                try
                {
                    Directory.Delete(mainProfile, true);
                    session.Log($"[OK] Deleted main profile folder: {mainProfile}");
                }
                catch (Exception ex)
                {
                    session.Log($"[WARN] Could not delete {mainProfile} (locked): {ex.Message}");"""

new1 = """            // 3. Delete main profile folder + stale SionyxUser.* / TEMP.* folders
            string mainProfile = System.IO.Path.Combine(@"C:\\Users", username);
            if (Directory.Exists(mainProfile))
            {
                // Force-unload user hive before delete (ntuser.dat / UsrClass.dat stay locked after logoff)
                try
                {
                    if (sid != null)
                    {
                        RunCommand("reg", $"unload \\"HKU\\\\{sid}\\"", session);
                        RunCommand("reg", $"unload \\"HKU\\\\{sid}_Classes\\"", session);
                        System.Threading.Thread.Sleep(1500);
                        session.Log("[INFO] Hive unload attempted before profile delete");
                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] Hive unload attempted\\n");
                    }
                }
                catch { }

                try
                {
                    int rmrc = RunCommand("cmd", $"/c rmdir /s /q \\"{mainProfile}\\"", session);
                    if (rmrc == 0)
                        session.Log($"[OK] Deleted main profile folder: {mainProfile}");
                    else
                        throw new Exception($"rmdir exit code {rmrc}");
                }
                catch (Exception ex)
                {
                    session.Log($"[WARN] Could not delete {mainProfile} (locked): {ex.Message}");"""

count1 = content.count(old1)
print(f"Fix1 matches: {count1}")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Fix1 OK")
else:
    print("Fix1 NOT FOUND — עצור ובדוק")

# ================================================================
# תיקון 2: PendingFileRenameOperations — writable + לוג כשל
# ================================================================
old2 = """                    try
                    {
                        using (var regKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                            .OpenSubKey(@"SYSTEM\\CurrentControlSet\\Control\\Session Manager", true))
                        {
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\\\\??\\\\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                        }
                    }
                    catch (Exception rex) { session.Log($"[WARN] PendingRename failed: {rex.Message}"); }"""

new2 = """                    try
                    {
                        using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                        using (var regKey = baseKey.OpenSubKey(@"SYSTEM\\CurrentControlSet\\Control\\Session Manager", writable: true))
                        {
                            if (regKey == null) throw new Exception("Session Manager key not found");
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\\\\??\\\\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename registered for {mainProfile}\\n");
                        }
                    }
                    catch (Exception rex)
                    {
                        session.Log($"[WARN] PendingRename failed: {rex.Message}");
                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename FAILED: {rex.Message}\\n");
                    }"""

count2 = content.count(old2)
print(f"Fix2 matches: {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix2 OK")
else:
    print("Fix2 NOT FOUND — עצור ובדוק")

# ================================================================
# תיקון 3: שחזר LimitBlankPasswordUse=1 ב-uninstall
# ================================================================
old3 = """            // 4. Disable AutoLogon
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
            catch (Exception ex) { session.Log($"[WARN] AutoLogon cleanup: {ex.Message}"); }"""

new3 = """            // 3b. Restore LimitBlankPasswordUse to system default (1)
            try
            {
                using (var lsaKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey(@"SYSTEM\\CurrentControlSet\\Control\\Lsa", true))
                {
                    lsaKey?.SetValue("LimitBlankPasswordUse", 1, RegistryValueKind.DWord);
                    session.Log("[OK] LimitBlankPasswordUse restored to 1");
                }
            }
            catch (Exception ex) { session.Log($"[WARN] LimitBlankPasswordUse restore: {ex.Message}"); }

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
            catch (Exception ex) { session.Log($"[WARN] AutoLogon cleanup: {ex.Message}"); }"""

count3 = content.count(old3)
print(f"Fix3 matches: {count3}")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("Fix3 OK")
else:
    print("Fix3 NOT FOUND — עצור ובדוק")

open(
    r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs',
    'w', encoding='utf-8'
).write(content)
print("SAVED")
