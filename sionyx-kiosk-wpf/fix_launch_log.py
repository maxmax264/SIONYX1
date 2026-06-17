content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            session.Log("=== LaunchKiosk: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"] ?? @"C:\\Program Files\\SIONYX\\";
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");

                if (!File.Exists(appExe))
                {
                    session.Log($"[WARN] Exe not found: {appExe}");
                    return ActionResult.Success;
                }

                var psi = new ProcessStartInfo
                {
                    FileName = appExe,
                    Arguments = "--kiosk",
                    UseShellExecute = true,
                };
                Process.Start(psi);
                session.Log($"[OK] Kiosk launched: {appExe}");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] LaunchKiosk failed (non-fatal): {ex.Message}");
                return ActionResult.Success;
            }
        }'''

new = '''        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            session.Log("=== LaunchKiosk: START ===");
            string logFile = @"C:\\Users\\user\\Desktop\\sionyx_launch.log";
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"] ?? @"C:\\Program Files\\SIONYX\\";
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");

                File.AppendAllText(logFile, $"[{DateTime.Now}] LaunchKiosk START\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] INSTALLDIR={installDir}\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] appExe={appExe}\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] Exe exists={File.Exists(appExe)}\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] CurrentUser={Environment.UserName}\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] SessionId={System.Diagnostics.Process.GetCurrentProcess().SessionId}\\n");
                session.Log($"[INFO] LaunchKiosk: appExe={appExe} exists={File.Exists(appExe)}");

                if (!File.Exists(appExe))
                {
                    session.Log($"[WARN] Exe not found: {appExe}");
                    File.AppendAllText(logFile, $"[{DateTime.Now}] ERROR: Exe not found\\n");
                    return ActionResult.Success;
                }

                var psi = new ProcessStartInfo
                {
                    FileName = appExe,
                    Arguments = "--kiosk",
                    UseShellExecute = true,
                };
                File.AppendAllText(logFile, $"[{DateTime.Now}] Calling Process.Start...\\n");
                var proc = Process.Start(psi);
                File.AppendAllText(logFile, $"[{DateTime.Now}] Process.Start returned: {(proc == null ? "null" : proc.Id.ToString())}\\n");
                session.Log($"[OK] Kiosk launched: {appExe} pid={proc?.Id}");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] LaunchKiosk failed: {ex.Message}");
                File.AppendAllText(logFile, $"[{DateTime.Now}] EXCEPTION: {ex.Message}\\n");
                File.AppendAllText(logFile, $"[{DateTime.Now}] StackTrace: {ex.StackTrace}\\n");
                return ActionResult.Success;
            }
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
