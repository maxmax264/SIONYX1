content = open(
    r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs',
    encoding='utf-8'
).read()

old2 = """                        using (var regKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                            .OpenSubKey(@"SYSTEM\\CurrentControlSet\\Control\\Session Manager", true))
                        {
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\\??\\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                        }
                    }
                    catch (Exception rex) { session.Log($"[WARN] PendingRename failed: {rex.Message}"); }"""

new2 = """                        using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                        using (var regKey = baseKey.OpenSubKey(@"SYSTEM\\CurrentControlSet\\Control\\Session Manager", writable: true))
                        {
                            if (regKey == null) throw new Exception("Session Manager key not found");
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\\??\\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename registered for {mainProfile}\n");
                        }
                    }
                    catch (Exception rex)
                    {
                        session.Log($"[WARN] PendingRename failed: {rex.Message}");
                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename FAILED: {rex.Message}\n");
                    }"""

count = content.count(old2)
print(f"Fix2 matches: {count}")
if count == 1:
    content = content.replace(old2, new2, 1)
    open(
        r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs',
        'w', encoding='utf-8'
    ).write(content)
    print("Fix2 OK — SAVED")
else:
    print("NOT FOUND — שלח פלט נוסף")
