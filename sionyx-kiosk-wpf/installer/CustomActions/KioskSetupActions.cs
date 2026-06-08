using System;
using System.Diagnostics;
using System.IO;
using System.Management;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32;
using WixToolset.Dtf.WindowsInstaller;

namespace SionyxInstaller
{
    /// <summary>
    /// WiX custom actions for SIONYX Kiosk installer.
    ///
    /// System registry changes (outside HKLM\SOFTWARE\SIONYX):
    ///   - Lsa\LimitBlankPasswordUse = 0  (required for blank-password user tiles)
    ///   - Per-user policies in SionyxUser's HKU hive only (never HKLM)
    ///
    /// No other system keys are modified. If a host machine has non-standard
    /// Windows configuration, that should be resolved separately.
    /// </summary>
    public class KioskSetupActions
    {
        private const string KioskUsername = "SionyxUser";
        private const string AppName = "SIONYX";
        private const string TaskName = "SIONYX Kiosk";

        [DllImport("userenv.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern int CreateProfile(
            string pszUserSid,
            string pszUserName,
            StringBuilder pszProfilePath,
            uint cchProfilePath);

        // ====================================================================
        //  INSTALL ACTIONS
        // ====================================================================

        /// <summary>
        /// Creates (or resets) the local SionyxUser account with a blank password.
        /// Sets LimitBlankPasswordUse=0 so credential providers show the account
        /// on the Windows sign-in screen.
        /// </summary>
        [CustomAction]
        public static ActionResult CreateKioskUser(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== CreateKioskUser: START ===");

            try
            {
                // Allow blank-password accounts to appear on login screen
                SetLimitBlankPasswordUse(session, enabled: false);

                // Clean up stale profile folders (SionyxUser.* and TEMP.*)
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

                bool exists = UserExists(KioskUsername, session);

                if (exists)
                {
                    session.Log($"User '{KioskUsername}' already exists — resetting password");
                    RunCommand("net", $"user \"{KioskUsername}\" \"\"", session);
                }
                else
                {
                    session.Log($"Creating new user '{KioskUsername}'...");
                    int rc = RunCommand("net",
                        $"user \"{KioskUsername}\" \"\" /add /fullname:\"SIONYX Kiosk User\" /comment:\"Restricted kiosk account\" /passwordchg:no",
                        session);

                    if (rc != 0)
                    {
                        session.Log($"[ERROR] Failed to create user (exit code {rc})");
                        return ActionResult.Failure;
                    }

                    SetPasswordNeverExpires(KioskUsername, session);
                }

                RunCommand("net", $"localgroup Administrators \"{KioskUsername}\" /delete", session);
                RunCommand("net", $"localgroup Users \"{KioskUsername}\" /add", session);

                // Skip OOBE for all new profiles on this machine
                try
                {
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var oobeKey = baseKey.CreateSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\FirstLogonCommands", true))
                    {
                        // No commands needed - just ensure key exists
                    }
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var oobeKey = baseKey.CreateSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE", true))
                    {
                        oobeKey.SetValue("SkipMachineOOBE", 1, RegistryValueKind.DWord);
                        oobeKey.SetValue("SkipUserOOBE", 1, RegistryValueKind.DWord);
                        session.Log("[OK] OOBE skip flags set in HKLM");
                    }
                }
                catch (Exception ex) { session.Log($"[WARN] OOBE skip: {ex.Message}"); }

                session.Log($"[OK] Kiosk user account ready ({sw.ElapsedMilliseconds}ms)");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] CreateKioskUser failed ({sw.ElapsedMilliseconds}ms): {ex}");
                return ActionResult.Failure;
            }
        }

        /// <summary>
        /// Applies kiosk lockdown policies to SionyxUser's per-user registry hive.
        /// Written to HKU\{SionyxUser}\... (NOT HKLM) so they only affect the
        /// kiosk account, never the machine owner.
        /// </summary>
        [CustomAction]
        public static ActionResult ApplySecurityRestrictions(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== ApplySecurityRestrictions: START ===");
            session.Log("[DBG] Profile check running");

            try
            {
                string hivePath = $@"C:\Users\{KioskUsername}\ntuser.dat";
                const string tempHiveKey = "SIONYX_TEMP_HIVE";

                if (!File.Exists(hivePath))
                {
                    session.Log($"[WARN] ntuser.dat not found at {hivePath} — skipping per-user policies");
                    return ActionResult.Success;
                }

                int loadResult = RunCommand("reg", $"load \"HKU\\{tempHiveKey}\" \"{hivePath}\"", session);
                if (loadResult != 0)
                {
                    session.Log("[WARN] Could not load user hive — skipping per-user policies");
                    return ActionResult.Success;
                }

                try
                {
                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                        "NoRun", 1);

                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                        "DisableRegistryTools", 1);

                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                        "DisableCMD", 2);

                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                        "DisableTaskMgr", 1);

                    // Skip Windows OOBE ("Getting Windows ready") on first logon
                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE",
                        "SkipUserOOBE", 1);
                    SetUserRegistryPolicy(session, tempHiveKey,
                        @"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE",
                        "SkipMachineOOBE", 1);

                    // Ensure .txt ShellNew exists so "New > Text Document" appears in context menu
                    using (var hku = RegistryKey.OpenBaseKey(RegistryHive.Users, RegistryView.Registry64))
                    using (var shellNewKey = hku.CreateSubKey($@"{tempHiveKey}\SOFTWARE\Classes\.txt\ShellNew"))
                    {
                        shellNewKey.SetValue("NullFile", "", RegistryValueKind.String);
                        session.Log("[OK] .txt ShellNew NullFile set for SionyxUser");
                    }
                    session.Log($"[OK] Security restrictions applied to {KioskUsername} only");
                }
                finally
                {
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                    RunCommand("reg", $"unload \"HKU\\{tempHiveKey}\"", session);
                }

                session.Log($"=== ApplySecurityRestrictions: DONE ({sw.ElapsedMilliseconds}ms) ===");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] ApplySecurityRestrictions failed ({sw.ElapsedMilliseconds}ms): {ex}");
                return ActionResult.Failure;
            }
        }

        /// <summary>
        /// Creates a scheduled task that launches SionyxKiosk.exe --kiosk
        /// when SionyxUser logs on.
        /// </summary>
        [CustomAction]
        public static ActionResult SetupAutoStart(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== SetupAutoStart: START ===");

            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");

                RunCommand("schtasks", "/delete /tn \"SIONYX Kiosk\" /f", session);

                string psScript =
                    $"$action = New-ScheduledTaskAction -Execute '{appExe}' -Argument '--kiosk'; " +
                    $"$trigger = New-ScheduledTaskTrigger -AtLogOn -User '{KioskUsername}'; " +
                    "$settings = New-ScheduledTaskSettingsSet " +
                        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable " +
                        "-ExecutionTimeLimit (New-TimeSpan -Hours 0) " +
                        "-RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1); " +
                    $"$principal = New-ScheduledTaskPrincipal -UserId '{KioskUsername}' -LogonType Interactive -RunLevel Limited; " +
                    "Register-ScheduledTask -TaskName 'SIONYX Kiosk' " +
                        "-Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force";

                int rc = RunCommand("powershell.exe",
                    $"-ExecutionPolicy Bypass -NoProfile -Command \"{psScript}\"",
                    session);

                if (rc != 0)
                    session.Log($"[WARN] Scheduled task creation returned exit code {rc}");

                session.Log($"[OK] Scheduled task created ({sw.ElapsedMilliseconds}ms)");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] SetupAutoStart failed ({sw.ElapsedMilliseconds}ms): {ex}");
                return ActionResult.Failure;
            }
        }

        /// <summary>
        /// Creates the SionyxUser Windows profile (via Win32 CreateProfile API)
        /// and sets up app directories + a startup shortcut.
        /// </summary>
        [CustomAction]
        public static ActionResult InitializeProfile(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== InitializeProfile: START ===");
                File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] InitializeProfile: START\n");

            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string profilePath = $@"C:\Users\{KioskUsername}";

                // Delete old profile folder before CreateProfile so it uses the correct path
                if (Directory.Exists(profilePath))
                {
                    // Unload SionyxUser registry hive before deleting (prevents UsrClass.dat lock)
                    try
                    {
                        string sidForUnload = GetUserSid(KioskUsername);
                        if (sidForUnload != null)
                        {
                            int unloadResult = RunCommand("reg", $"unload \"HKU\\{sidForUnload}\"", session);
                            session.Log($"[INFO] reg unload result: {unloadResult}");
                            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] reg unload result={unloadResult}\n");
                            System.Threading.Thread.Sleep(500);
                        }
                    }
                    catch (Exception ex)
                    {
                        session.Log($"[WARN] reg unload failed: {ex.Message}");
                        File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] reg unload failed: {ex.Message}\n");
                    }
                    try
                    {
                        int rmResult = RunCommand("cmd", $"/c rmdir /s /q \"{profilePath}\"", session);
                        if (rmResult == 0)
                        {
                            session.Log($"[OK] Deleted old profile folder: {profilePath}");
                            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] Deleted old profile folder\n");
                        }
                        else
                        {
                            session.Log($"[WARN] rmdir returned {rmResult} - continuing anyway");
                            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] WARNING: rmdir failed, continuing\n");
                        }
                    }
                    catch (Exception ex)
                    {
                        session.Log($"[WARN] Could not delete profile folder: {ex.Message} - continuing");
                        File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] WARNING: could not delete profile folder\n");
                    }
                }

                // Create the profile via Win32 API so Windows does not show "Getting Windows ready"
                var profilePathBuilder = new StringBuilder(260);
                string userSid = GetUserSid(KioskUsername);
                if (userSid != null)
                {
                    int cpResult = CreateProfile(userSid, KioskUsername, profilePathBuilder, (uint)profilePathBuilder.Capacity);
                    session.Log($"[INFO] CreateProfile API result: {cpResult} path: {profilePathBuilder}");
                    File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] CreateProfile result={cpResult} path={profilePathBuilder}\n");
                }
                else
                {
                    session.Log("[WARN] Could not get SID for CreateProfile — skipping API call");
                }

                // Ensure ProfileList registry entry exists regardless
                // Clean up stale ProfileList entries before creating new one
                using (var baseKeyClean = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var profileListKey = baseKeyClean.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList", true))
                {
                    if (profileListKey != null)
                    {
                        foreach (var subKeyName in profileListKey.GetSubKeyNames())
                        {
                            if (subKeyName.EndsWith(".bak"))
                            {
                                profileListKey.DeleteSubKeyTree(subKeyName, false);
                                session.Log($"[OK] Removed stale ProfileList entry: {subKeyName}");
                            }
                            else
                            {
                                using (var sk = profileListKey.OpenSubKey(subKeyName))
                                {
                                    if (sk != null && sk.GetValue("ProfileImagePath") == null)
                                    {
                                        profileListKey.DeleteSubKeyTree(subKeyName, false);
                                        session.Log($"[OK] Removed empty ProfileList entry: {subKeyName}");
                                    }
                                }
                            }
                        }
                    }
                }
                string profileSid = GetUserSid(KioskUsername);
                if (profileSid != null)
                {
                    string profileRegPath = $@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{profileSid}";
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var profileKey = baseKey.CreateSubKey(profileRegPath, true))
                    {
                        if (profileKey.GetValue("ProfileImagePath") == null)
                        {
                            profileKey.SetValue("ProfileImagePath", $@"C:\Users\{KioskUsername}", RegistryValueKind.ExpandString);
                            profileKey.SetValue("Flags", 0, RegistryValueKind.DWord);
                            profileKey.SetValue("State", 0, RegistryValueKind.DWord);
                            session.Log($"[OK] ProfileList registry entry created for SID {profileSid}");
                            profileKey.SetValue("FullProfile", 1, RegistryValueKind.DWord);
                            profileKey.SetValue("RunLogonScriptSync", 0, RegistryValueKind.DWord);
                        }
                        else
                        {
                            session.Log($"[OK] ProfileList registry entry already exists for SID {profileSid}");
                        }
                    }
                }

                string startupPath = Path.Combine(profilePath,
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup");
                string sionyxDir = Path.Combine(profilePath, ".sionyx");
                string logsDir = Path.Combine(profilePath, @"AppData\Local\SIONYX\logs");

                // Create all standard Windows profile directories
                var standardDirs = new[]
                {
                    @"Desktop",
                    @"Documents",
                    @"Downloads",
                    @"Pictures",
                    @"Music",
                    @"Videos",
                    @"AppData\Local",
                    @"AppData\Local\Microsoft\Windows",
                    @"AppData\Local\Temp",
                    @"AppData\LocalLow",
                    @"AppData\Roaming",
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup",
                };
                foreach (var dir in standardDirs)
                    Directory.CreateDirectory(Path.Combine(profilePath, dir));
                Directory.CreateDirectory(sionyxDir);
                Directory.CreateDirectory(logsDir);
                session.Log("[OK] Profile directories created");
                File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] Profile dirs created\n");

                string shortcutPath = Path.Combine(startupPath, "SIONYX.lnk");
                string targetExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string iconPath = Path.Combine(installDir, "app-logo.ico");
                CreateShortcut(shortcutPath, targetExe, "--kiosk", iconPath, session);
                session.Log($"[OK] Startup shortcut created ({sw.ElapsedMilliseconds}ms)");

                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] InitializeProfile failed ({sw.ElapsedMilliseconds}ms): {ex}");
                return ActionResult.Failure;
            }
        }

        /// <summary>
        /// Post-install verification: checks user, profile, task, exe, and registry.
        /// Writes results to install.log. Only shows a MessageBox if errors are found;
        /// on success, the WiX finish page shows next steps.
        /// </summary>
        [CustomAction]
        public static ActionResult VerifyInstallation(Session session)
        {
            session.Log("=== VerifyInstallation: START ===");

            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string logFile = Path.Combine(installDir, "install.log");
                var errors = new System.Collections.Generic.List<string>();
                var log = new StringBuilder();

                void Log(string msg)
                {
                    session.Log(msg);
                    log.AppendLine(msg);
                }

                string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                Log("");
                Log("============================================");
                Log($"  POST-INSTALL VERIFICATION ({timestamp})");
                Log("============================================");

                // 1. User account
                if (UserExists(KioskUsername, session))
                    Log($"[PASS] User account {KioskUsername} exists");
                else
                {
                    Log($"[FAIL] User account {KioskUsername} NOT FOUND");
                    errors.Add($"User account {KioskUsername} was not created");
                }

                // 2. Profile directory
                string profilePath = $@"C:\Users\{KioskUsername}";
                if (Directory.Exists(profilePath))
                    Log($"[PASS] Profile directory exists: {profilePath}");
                else
                {
                    Log($"[FAIL] Profile directory MISSING: {profilePath}");
                    errors.Add("User profile directory was not created");
                }

                // 3. Profile registry (ProfileList)
                string sid = GetUserSid(KioskUsername);
                if (sid != null)
                {
                    string regPath = $@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{sid}";
                    using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                                .OpenSubKey(regPath))
                    {
                        if (key != null)
                            Log($"[PASS] Profile registry entry exists (SID: {sid})");
                        else
                        {
                            Log($"[FAIL] Profile registry entry MISSING for SID {sid}");
                            errors.Add("ProfileList registry entry not found");
                        }
                    }
                }

                // 4. Scheduled task
                int taskCheck = RunCommand("schtasks", "/query /tn \"SIONYX Kiosk\"", session);
                if (taskCheck == 0)
                    Log("[PASS] Scheduled task SIONYX Kiosk exists");
                else
                {
                    Log("[FAIL] Scheduled task SIONYX Kiosk NOT FOUND");
                    errors.Add("Scheduled task was not created");
                }

                // 5. App executable
                string exePath = Path.Combine(installDir, "SionyxKiosk.exe");
                if (File.Exists(exePath))
                    Log($"[PASS] App executable: {exePath}");
                else
                {
                    Log($"[FAIL] App executable MISSING: {exePath}");
                    errors.Add("Application executable was not installed");
                }

                // 6. Startup shortcut
                string startupLnk = Path.Combine(profilePath,
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\SIONYX.lnk");
                if (File.Exists(startupLnk))
                    Log($"[PASS] Startup shortcut exists for {KioskUsername}");
                else
                    Log("[WARN] Startup shortcut not found at expected path");

                // 7. Registry configuration
                string[] regKeys = { "Install_Dir", "Version", "OrgId", "FirebaseProjectId", "KioskUsername" };
                var missingKeys = new System.Collections.Generic.List<string>();
                using (var appKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey($@"SOFTWARE\{AppName}"))
                {
                    foreach (string keyName in regKeys)
                    {
                        if (appKey?.GetValue(keyName) == null)
                            missingKeys.Add(keyName);
                    }
                }

                if (missingKeys.Count == 0)
                    Log("[PASS] All registry configuration keys present");
                else
                {
                    Log($"[FAIL] Missing registry keys: {string.Join(", ", missingKeys)}");
                    errors.Add($"Registry configuration incomplete — missing: {string.Join(", ", missingKeys)}");
                }

                // 8. LimitBlankPasswordUse
                using (var lsaKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Lsa"))
                {
                    int lbp = (int?)lsaKey?.GetValue("LimitBlankPasswordUse") ?? -1;
                    if (lbp == 0)
                        Log("[PASS] LimitBlankPasswordUse = 0 (blank-password tiles enabled)");
                    else
                    {
                        Log($"[FAIL] LimitBlankPasswordUse = {lbp} (expected 0)");
                        errors.Add($"LimitBlankPasswordUse is {lbp}, must be 0 for SionyxUser to appear on login screen");
                    }
                }

                // Summary
                Log("");
                Log("--------------------------------------------");
                if (errors.Count == 0)
                    Log("[OK] ALL CHECKS PASSED — Installation verified successfully!");
                else
                {
                    Log($"[ERROR] Installation completed with {errors.Count} error(s):");
                    foreach (string e in errors)
                        Log($"    - {e}");
                }
                Log("--------------------------------------------");

                try { File.WriteAllText(logFile, log.ToString()); }
                catch { session.Log("[WARN] Could not write install.log"); }

                // Only show a MessageBox if verification found errors.
                // On success, the WiX finish page shows next steps — no popup needed.
                if (errors.Count > 0)
                {
                    string uiLevelStr = session.CustomActionData.ContainsKey("UILEVEL")
                        ? session.CustomActionData["UILEVEL"] : "5";
                    bool isSilent = int.TryParse(uiLevelStr, out int uiLevel) && uiLevel <= 3;

                    if (!isSilent)
                    {
                        try
                        {
                            string summary = $"{errors.Count} CHECK(S) FAILED\n\n" +
                                string.Join("\n", errors) +
                                $"\n\nFull log: {logFile}";

                            MessageBoxFromInstaller(
                                "SIONYX — Install Issues Detected",
                                summary,
                                0x00000030u); // WARNING icon
                        }
                        catch (Exception mbEx)
                        {
                            session.Log($"[WARN] Could not show MessageBox: {mbEx.Message}");
                        }
                    }
                }

                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] VerifyInstallation failed: {ex}");
                return ActionResult.Success;
            }
        }


        /// <summary>
        /// Sets up AutoLogon for SionyxUser once, so Windows creates a full profile on first boot.
        /// A first-logon script disables AutoLogon after the profile is created.
        /// </summary>
        [CustomAction]
        public static ActionResult SetupFirstLogon(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== SetupFirstLogon: START ===");
                File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] SetupFirstLogon: START\n");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];

                // Write a PowerShell script that runs on first logon and disables AutoLogon
                string scriptContent = @"
# Disable AutoLogon after first logon
reg delete ""HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"" /v AutoAdminLogon /f 2>$null
reg delete ""HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"" /v DefaultPassword /f 2>$null
reg delete ""HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"" /v AutoLogonCount /f 2>$null
# Remove this script from startup
schtasks /delete /tn ""SIONYX_FirstLogon"" /f 2>$null
";
                string scriptPath = System.IO.Path.Combine(installDir, "first_logon.ps1");
                File.WriteAllText(scriptPath, scriptContent);
                session.Log("[OK] First logon script written to: " + scriptPath);

                // Create scheduled task to run script on first logon of SionyxUser
                string psCmd = "-ExecutionPolicy Bypass -WindowStyle Hidden -File \"" + scriptPath + "\"";
                string fullCmd = "$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '" + psCmd + "'; " +
                    "$trigger = New-ScheduledTaskTrigger -AtLogOn -User 'SionyxUser'; " +
                    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries; " +
                    "$principal = New-ScheduledTaskPrincipal -UserId 'SionyxUser' -LogonType Interactive -RunLevel Highest; " +
                    "Register-ScheduledTask -TaskName 'SIONYX_FirstLogon' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force";

                int rc = RunCommand("powershell.exe", "-ExecutionPolicy Bypass -NoProfile -Command \"" + fullCmd + "\"", session);
                session.Log("[OK] First logon task created, exit=" + rc);

                // Enable AutoLogon for SionyxUser (one time)
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                {
                    key.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                    key.SetValue("DefaultUserName", "SionyxUser", RegistryValueKind.String);
                    key.SetValue("DefaultPassword", "", RegistryValueKind.String);
                    key.SetValue("AutoLogonCount", 1, RegistryValueKind.DWord);
                    key.SetValue("EnableFirstLogonAnimation", 1, RegistryValueKind.DWord);
                    session.Log("[OK] AutoLogon configured for SionyxUser (1 time)");
                    File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] AutoLogon configured\n");
                }

                session.Log("=== SetupFirstLogon: DONE (" + sw.ElapsedMilliseconds + "ms) ===");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log("[ERROR] SetupFirstLogon failed: " + ex.Message);
                return ActionResult.Failure;
            }
        }

        // ====================================================================
        //  UNINSTALL ACTIONS
        // ====================================================================

        [CustomAction]
        public static ActionResult StopProcesses(Session session)
        {
            session.Log("=== StopProcesses: START ===");
            try
            {
                int rc = RunCommand("taskkill", "/F /IM SionyxKiosk.exe", session);
                session.Log(rc == 0 ? "[OK] SionyxKiosk terminated" : "[INFO] SionyxKiosk was not running");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] StopProcesses: {ex.Message}");
                return ActionResult.Success;
            }
        }

        [CustomAction]
        public static ActionResult RemoveScheduledTask(Session session)
        {
            session.Log("=== RemoveScheduledTask: START ===");
            try
            {
                int rc = RunCommand("schtasks", "/delete /tn \"SIONYX Kiosk\" /f", session);
                session.Log(rc == 0 ? "[OK] Scheduled task removed" : "[INFO] Scheduled task not found");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] RemoveScheduledTask: {ex.Message}");
                return ActionResult.Success;
            }
        }

        [CustomAction]
        public static ActionResult RevertSecurity(Session session)
        {
            session.Log("=== RevertSecurity: START ===");
            try
            {
                // Remove any machine-wide policies (from older installs that used HKLM)
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoRun");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableCMD");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr");

                session.Log("[OK] Security restrictions reverted");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] RevertSecurity: {ex.Message}");
                return ActionResult.Success;
            }
        }

        [CustomAction]
        public static ActionResult RemoveKioskUser(Session session)
        {
            session.Log("=== RemoveKioskUser: START ===");
            try
            {
                RemoveUserAndProfile(KioskUsername, session);
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] RemoveKioskUser: {ex.Message}");
                return ActionResult.Success;
            }
        }

        // ====================================================================
        //  HELPERS
        // ====================================================================

        /// <summary>
        /// Sets LimitBlankPasswordUse. When disabled (value=0), Windows credential
        /// providers show blank-password accounts on the sign-in screen.
        /// This is the only system registry value the installer modifies.
        /// </summary>
        private static void SetLimitBlankPasswordUse(Session session, bool enabled)
        {
            try
            {
                using (var lsaKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Lsa", true))
                {
                    if (lsaKey == null)
                    {
                        session.Log("[ERROR] Cannot open HKLM\\SYSTEM\\...\\Lsa");
                        return;
                    }

                    int value = enabled ? 1 : 0;
                    lsaKey.SetValue("LimitBlankPasswordUse", value, RegistryValueKind.DWord);
                    session.Log($"[OK] LimitBlankPasswordUse = {value}");
                }
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] LimitBlankPasswordUse: {ex.Message}");
            }
        }

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        private static extern int MessageBoxW(IntPtr hWnd, string text, string caption, uint type);

        private static void MessageBoxFromInstaller(string title, string text, uint type)
        {
            MessageBoxW(IntPtr.Zero, text, title, type | 0x00040000); // MB_TOPMOST
        }

        private static string ResolvePath(string fileName)
        {
            if (Path.IsPathRooted(fileName)) return fileName;

            string sysDir = Environment.GetFolderPath(Environment.SpecialFolder.System);
            string withExe = Path.HasExtension(fileName) ? fileName : fileName + ".exe";

            string sys = Path.Combine(sysDir, withExe);
            if (File.Exists(sys)) return sys;

            string wbem = Path.Combine(sysDir, "wbem", withExe);
            if (File.Exists(wbem)) return wbem;

            return fileName;
        }

        private static int RunCommand(string fileName, string arguments, Session session, int timeoutMs = 60000)
        {
            var resolvedPath = ResolvePath(fileName);
            session.Log($"  [CMD] {resolvedPath} {arguments}");
            var sw = Stopwatch.StartNew();

            var psi = new ProcessStartInfo
            {
                FileName = resolvedPath,
                Arguments = arguments,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using (var process = Process.Start(psi))
            {
                var stderrBuilder = new StringBuilder();
                process.ErrorDataReceived += (s, e) =>
                {
                    if (e.Data != null) stderrBuilder.AppendLine(e.Data);
                };
                process.BeginErrorReadLine();

                string stdout = process.StandardOutput.ReadToEnd();

                bool exited = process.WaitForExit(timeoutMs);
                sw.Stop();

                if (!exited)
                {
                    session.Log($"  [TIMEOUT] Command did not finish in {timeoutMs}ms — killing process");
                    try { process.Kill(); } catch { /* best effort */ }
                    return -1;
                }

                if (!string.IsNullOrWhiteSpace(stdout))
                    session.Log($"  [STDOUT] {stdout.TrimEnd()}");

                string stderr = stderrBuilder.ToString();
                if (!string.IsNullOrWhiteSpace(stderr) && process.ExitCode != 0)
                    session.Log($"  [STDERR] {stderr.TrimEnd()}");

                session.Log($"  [CMD] exit={process.ExitCode} elapsed={sw.ElapsedMilliseconds}ms");
                return process.ExitCode;
            }
        }

        private static void SetPasswordNeverExpires(string username, Session session)
        {
            string wmic = ResolvePath("wmic");
            if (File.Exists(wmic))
            {
                RunCommand("wmic",
                    $"useraccount where name=\"{username}\" set PasswordExpires=false",
                    session);
            }
            else
            {
                RunCommand("powershell.exe",
                    $"-NoProfile -Command \"Set-LocalUser -Name '{username}' -PasswordNeverExpires $true\"",
                    session);
            }
        }

        private static bool UserExists(string username, Session session)
        {
            return RunCommand("net", $"user \"{username}\"", session) == 0;
        }

        private static string GetUserSid(string username)
        {
            try
            {
                var account = new NTAccount(username);
                var sid = (SecurityIdentifier)account.Translate(typeof(SecurityIdentifier));
                return sid.Value;
            }
            catch
            {
                return null;
            }
        }

        private static void SetUserRegistryPolicy(Session session, string hiveKey, string subKey, string name, int value)
        {
            using (var hku = RegistryKey.OpenBaseKey(RegistryHive.Users, RegistryView.Registry64))
            using (var key = hku.CreateSubKey($@"{hiveKey}\{subKey}"))
            {
                key.SetValue(name, value, RegistryValueKind.DWord);
                session.Log($"  Set {name} = {value} (per-user)");
            }
        }

        private static void RemoveRegistryPolicy(Session session, string subKey, string name)
        {
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                            .OpenSubKey(subKey, true))
                {
                    if (key?.GetValue(name) != null)
                    {
                        key.DeleteValue(name);
                        session.Log($"  Removed policy: {name}");
                    }
                }
            }
            catch
            {
                session.Log($"  Policy not set: {name}");
            }
        }

        private static void CreateShortcut(string shortcutPath, string targetPath, string arguments, string iconPath, Session session)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic shortcut = shell.CreateShortcut(shortcutPath);
                shortcut.TargetPath = targetPath;
                shortcut.Arguments = arguments;
                shortcut.IconLocation = iconPath + ",0";
                shortcut.Save();
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] CreateShortcut failed: {ex.Message}");
            }
        }

        private static void RemoveUserAndProfile(string username, Session session)
        {
            session.Log($"=== RemoveUserAndProfile: cleaning everything for {username} ===");
            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] === UNINSTALL START for {username} ===\n");
            string sid = GetUserSid(username);
            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] SID={sid}\n");

            // 1. Delete user account
            if (UserExists(username, session))
            {
                RunCommand("net", $"user \"{username}\" /delete", session);
                session.Log($"[OK] User account '{username}' deleted");
            }
            else
            {
                session.Log($"[INFO] User '{username}' not found — skipping");
            }

            // 2. Delete ProfileList entries (normal + .bak)
            if (sid != null)
            {
                foreach (var suffix in new[] { "", ".bak" })
                {
                    string regPath = $@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{sid}{suffix}";
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

            // 3. Delete main profile folder + stale SionyxUser.* / TEMP.* folders
            string mainProfile = System.IO.Path.Combine(@"C:\Users", username);
            if (Directory.Exists(mainProfile))
            {
                // Force-unload user hive before delete (ntuser.dat / UsrClass.dat stay locked after logoff)
                try
                {
                    if (sid != null)
                    {
                        RunCommand("reg", $"unload \"HKU\\{sid}\"", session);
                        RunCommand("reg", $"unload \"HKU\\{sid}_Classes\"", session);
                        System.Threading.Thread.Sleep(1500);
                        session.Log("[INFO] Hive unload attempted before profile delete");
                        File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] Hive unload attempted\n");
                    }
                }
                catch { }

                try
                {
                    int rmrc = RunCommand("cmd", $"/c rmdir /s /q \"{mainProfile}\"", session);
                    if (rmrc == 0)
                        session.Log($"[OK] Deleted main profile folder: {mainProfile}");
                    else
                        throw new Exception($"rmdir exit code {rmrc}");
                }
                catch (Exception ex)
                {
                    session.Log($"[WARN] Could not delete {mainProfile} (locked): {ex.Message}");
                    try
                    {
                        using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                        using (var regKey = baseKey.OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Session Manager", writable: true))
                        {
                            if (regKey == null) throw new Exception("Session Manager key not found");
                            var existing = regKey.GetValue("PendingFileRenameOperations") as string[] ?? new string[0];
                            var newList = new System.Collections.Generic.List<string>(existing);
                            newList.Add(@"\??\" + mainProfile);
                            newList.Add("");
                            regKey.SetValue("PendingFileRenameOperations", newList.ToArray(), RegistryValueKind.MultiString);
                            session.Log($"[OK] Scheduled {mainProfile} for deletion on next reboot");
                            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] PendingRename registered for {mainProfile}
");
                        }
                    }
                    catch (Exception rex)
                    {
                        session.Log($"[WARN] PendingRename failed: {rex.Message}");
                        File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] PendingRename FAILED: {rex.Message}
");
                    }
                }
            }
            string usersDir = @"C:\Users";
            foreach (var dir in Directory.GetDirectories(usersDir))
            {
                string name = Path.GetFileName(dir);
                if (name.StartsWith(username + ".") || name.StartsWith("TEMP."))
                {
                    try
                    {
                        Directory.Delete(dir, true);
                        session.Log($"[OK] Deleted folder: {name}");
                    }
                    catch
                    {
                        RunCommand("cmd", $"/c rmdir /s /q \"{dir}\"", session);
                        session.Log($"[OK] Deleted folder via cmd: {name}");
                    }
                }
            }

            // 3b. Restore LimitBlankPasswordUse to system default (1)
            try
            {
                using (var lsaKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Lsa", true))
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
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
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
            // 4. Clean AutoLogon registry entries
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                {
                    if (key != null)
                    {
                        key.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                        try { key.DeleteValue("DefaultPassword", false); } catch { }
                        try { key.DeleteValue("DefaultUserName", false); } catch { }
                        try { key.DeleteValue("AutoLogonSID", false); } catch { }
                        try { key.DeleteValue("AutoLogonCount", false); } catch { }
                        try { key.DeleteValue("EnableFirstLogonAnimation", false); } catch { }
                        session.Log("[OK] AutoLogon cleaned");
                    }
                }
            }
            catch (Exception ex) { session.Log($"[WARN] AutoLogon cleanup: {ex.Message}"); }

            // 5. Clean SpecialAccounts
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                    .OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList", true))
                {
                    if (key != null)
                    {
                        try { key.DeleteValue(username, false); } catch { }
                        session.Log("[OK] SpecialAccounts cleaned");
                    }
                }
            }
            catch (Exception ex) { session.Log($"[WARN] SpecialAccounts cleanup: {ex.Message}"); }

            // 6. Remove scheduled tasks
            RunCommand("schtasks", "/delete /tn \"SIONYX_FirstLogon\" /f", session);
            session.Log("[OK] SIONYX_FirstLogon task removed (if existed)");

            session.Log("=== RemoveUserAndProfile: DONE ===");
            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] === UNINSTALL DONE ===\n");
            // Check what remains
            bool folderExists = System.IO.Directory.Exists($@"C:\Users\{username}");
            bool userExists = false;
            try { new System.Security.Principal.NTAccount(username).Translate(typeof(System.Security.Principal.SecurityIdentifier)); userExists = true; } catch { }
            File.AppendAllText(@"C:\Users\user\Desktop\sionyx_debug.log", $"[{DateTime.Now}] After cleanup — folder exists: {folderExists}, user exists: {userExists}\n");
        }
    }
}



