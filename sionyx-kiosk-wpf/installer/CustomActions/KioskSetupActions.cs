using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32;
using WixToolset.Dtf.WindowsInstaller;

namespace SionyxInstaller
{
    public class KioskSetupActions
    {
        private const string AppName = "SIONYX";
        private const string RunKeyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run";
        private const string RunValueName = "SIONYX";

        [CustomAction]
        public static ActionResult SetupAutoStart(Session session)
        {
            var sw = Stopwatch.StartNew();
            session.Log("=== SetupAutoStart: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string runValue = $"\"{appExe}\" --kiosk";
                using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var runKey = baseKey.OpenSubKey(RunKeyPath, true))
                {
                    if (runKey == null) { session.Log("[ERROR] Could not open HKLM Run key"); return ActionResult.Failure; }
                    runKey.SetValue(RunValueName, runValue, RegistryValueKind.String);
                    session.Log($"[OK] HKLM Run set: {runValue}");
                }
                // Configure Auto-login for kiosk user
                try
                {
                    using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    using (var winlogon = baseKey.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                    {
                        if (winlogon != null)
                        {
                            winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                            winlogon.DeleteValue("DefaultPassword", false);
                            session.Log("[OK] Auto-login configured");
                        }
                    }
                }
                catch (Exception ex) { session.Log($"[WARN] Auto-login setup failed: {ex.Message}"); }

                session.Log($"=== SetupAutoStart: DONE ({sw.ElapsedMilliseconds}ms) ===");
                return ActionResult.Success;
            }
            catch (Exception ex) { session.Log($"[ERROR] SetupAutoStart failed: {ex}"); return ActionResult.Failure; }
        }

        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            string logFile = @"C:\Users\Public\Documents\SIONYX\launch_kiosk.log";
            try { Directory.CreateDirectory(Path.GetDirectoryName(logFile)); } catch { }
            Action<string> Log = msg => { session.Log(msg); try { File.AppendAllText(logFile, DateTime.Now.ToString("HH:mm:ss") + " " + msg + "\r\n"); } catch { } };
            Log("=== LaunchKiosk: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"] ?? @"C:\Program Files\SIONYX\";
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                Log($"[INFO] appExe={appExe} exists={File.Exists(appExe)}");
                if (!File.Exists(appExe)) { Log("[WARN] Exe not found"); return ActionResult.Success; }
                // Run SIONYX_LaunchOnce task as the logged-in user
                var r2 = RunCommand("schtasks", "/run /tn \"SIONYX_LaunchOnce\"", session);
                Log($"[INFO] schtasks /run result: {r2}");
                Log(r2 == 0 ? "[OK] LaunchOnce task triggered" : "[WARN] LaunchOnce task failed");
                return ActionResult.Success;
            }
            catch (Exception ex) { Log($"[WARN] LaunchKiosk failed: {ex.Message}"); return ActionResult.Success; }
        }

        [CustomAction]
        public static ActionResult VerifyInstallation(Session session)
        {
            session.Log("=== VerifyInstallation: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                var errors = new System.Collections.Generic.List<string>();
                var log = new StringBuilder();
                void Log(string msg) { session.Log(msg); log.AppendLine(msg); }
                Log($"POST-INSTALL VERIFICATION ({DateTime.Now:yyyy-MM-dd HH:mm:ss})");
                string exePath = Path.Combine(installDir, "SionyxKiosk.exe");
                if (File.Exists(exePath)) Log($"[PASS] Exe exists: {exePath}");
                else { Log($"[FAIL] Exe missing: {exePath}"); errors.Add("Exe missing"); }
                string[] regKeys = { "Install_Dir", "Version", "OrgId", "FirebaseProjectId" };
                using (var appKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64).OpenSubKey($@"SOFTWARE\{AppName}"))
                {
                    var missing = new System.Collections.Generic.List<string>();
                    foreach (var k in regKeys) if (appKey?.GetValue(k) == null) missing.Add(k);
                    if (missing.Count == 0) Log("[PASS] Registry keys OK");
                    else { Log($"[FAIL] Missing registry keys: {string.Join(", ", missing)}"); errors.Add($"Missing: {string.Join(", ", missing)}"); }
                }
                using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var runKey = baseKey.OpenSubKey(RunKeyPath))
                {
                    var val = runKey?.GetValue(RunValueName) as string;
                    if (!string.IsNullOrEmpty(val)) Log($"[PASS] HKLM Run entry exists: {val}");
                    else { Log("[FAIL] HKLM Run entry missing"); errors.Add("Run entry missing"); }
                }
                Log(errors.Count == 0 ? "[OK] ALL CHECKS PASSED" : $"[ERROR] {errors.Count} check(s) failed");
                try { File.WriteAllText(Path.Combine(installDir, "install.log"), log.ToString()); } catch { }
                return ActionResult.Success;
            }
            catch (Exception ex) { session.Log($"[ERROR] VerifyInstallation failed: {ex}"); return ActionResult.Success; }
        }

        [CustomAction]
        public static ActionResult SetupUpdateTask(Session session)
        {
            session.Log("=== SetupUpdateTask: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string triggerFile = Path.Combine(@"C:\Users\Public\Documents\SIONYX\updates", "pending_update.txt");
                string scriptPath = Path.Combine(installDir, "run_update.bat");
                string scriptContent = $@"@echo off
setlocal enabledelayedexpansion
set LOGFILE=C:\Users\Public\Documents\SIONYX\update_bat.log
echo %DATE% %TIME% BAT started >> ""%LOGFILE%""
if exist ""{triggerFile}"" (
    echo %DATE% %TIME% DEBUG raw file dump: >> ""%LOGFILE%""
    certutil -encodehex ""{triggerFile}"" ""{triggerFile}.hex"" >> ""%LOGFILE%"" 2>&1
    type ""{triggerFile}.hex"" >> ""%LOGFILE%""
    del ""{triggerFile}.hex"" 2>nul
    for /f ""usebackq delims="" %%i in (""{triggerFile}"") do set MSI_PATH=%%i
    echo %DATE% %TIME% MSI_PATH=!MSI_PATH! >> ""%LOGFILE%""
    taskkill /f /im SionyxKiosk.exe 2>nul
    timeout /t 5 /nobreak >nul
    taskkill /f /im SionyxKiosk.exe 2>nul
    timeout /t 5 /nobreak >nul
    echo %DATE% %TIME% Running msiexec >> ""%LOGFILE%""
    msiexec /i ""!MSI_PATH!"" /quiet /norestart
    echo %DATE% %TIME% msiexec done, exit=%ERRORLEVEL% >> ""%LOGFILE%""
    schtasks /run /tn ""SIONYX_LaunchOnce""
    echo %DATE% %TIME% schtasks run done, exit=%ERRORLEVEL% >> ""%LOGFILE%""
    del ""{triggerFile}""
    timeout /t 3 /nobreak >nul
) else (
    echo %DATE% %TIME% trigger file not found >> ""%LOGFILE%""
)
";
                File.WriteAllText(scriptPath, scriptContent);
                session.Log($"[OK] Update script created: {scriptPath}");

                string taskXml = $@"<?xml version=""1.0"" encoding=""UTF-16""?>
<Task version=""1.2"" xmlns=""http://schemas.microsoft.com/windows/2004/02/mit/task"">
  <Principals><Principal id=""Author""><UserId>S-1-5-18</UserId><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><ExecutionTimeLimit>PT30M</ExecutionTimeLimit><Priority>7</Priority></Settings>
  <Triggers><TimeTrigger><Repetition><Interval>PT1M</Interval><StopAtDurationEnd>false</StopAtDurationEnd></Repetition><StartBoundary>2000-01-01T00:00:00</StartBoundary><Enabled>true</Enabled></TimeTrigger></Triggers>
  <Actions Context=""Author""><Exec><Command>{scriptPath}</Command></Exec></Actions>
</Task>";
                string xmlPath = Path.Combine(Path.GetTempPath(), "sionyx_update_task.xml");
                File.WriteAllText(xmlPath, taskXml, System.Text.Encoding.Unicode);
                RunCommand("schtasks", $"/create /tn \"SIONYX_Update\" /xml \"{xmlPath}\" /f", session);
                session.Log("[OK] SIONYX_Update scheduled task created");
                try { File.Delete(xmlPath); } catch { }

                var query = new System.Management.ObjectQuery("SELECT UserName FROM Win32_ComputerSystem");
                var searcher = new System.Management.ManagementObjectSearcher(query);
                string currentUser = Environment.UserName;
                foreach (System.Management.ManagementObject mo in searcher.Get()) { currentUser = mo["UserName"]?.ToString() ?? currentUser; break; }
                session.Log($"[LaunchOnce] Running as user: {currentUser}");

                string launchTaskXml = $@"<?xml version=""1.0"" encoding=""UTF-16""?>
<Task version=""1.2"" xmlns=""http://schemas.microsoft.com/windows/2004/02/mit/task"">
  <Principals><Principal id=""Author""><UserId>{currentUser}</UserId><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries></Settings>
  <Triggers/>
  <Actions Context=""Author""><Exec><Command>{appExe}</Command><Arguments>--kiosk</Arguments></Exec></Actions>
</Task>";
                string launchXmlPath = Path.Combine(Path.GetTempPath(), "sionyx_launch_task.xml");
                File.WriteAllText(launchXmlPath, launchTaskXml, System.Text.Encoding.Unicode);
                RunCommand("schtasks", $"/create /tn \"SIONYX_LaunchOnce\" /xml \"{launchXmlPath}\" /f", session);
                session.Log("[OK] SIONYX_LaunchOnce scheduled task created");
                try { File.Delete(launchXmlPath); } catch { }
                return ActionResult.Success;
            }
            catch (Exception ex) { session.Log($"[WARN] SetupUpdateTask failed: {ex.Message}"); return ActionResult.Success; }
        }

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
            catch (Exception ex) { session.Log($"[WARN] StopProcesses: {ex.Message}"); return ActionResult.Success; }
        }

        [CustomAction]
        public static ActionResult RemoveAutoStart(Session session)
        {
            session.Log("=== RemoveAutoStart: START ===");
            try
            {
                using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var runKey = baseKey.OpenSubKey(RunKeyPath, true))
                {
                    if (runKey?.GetValue(RunValueName) != null) { runKey.DeleteValue(RunValueName, false); session.Log("[OK] HKLM Run entry removed"); }
                    else session.Log("[INFO] HKLM Run entry not found");
                }
                return ActionResult.Success;
            }
            catch (Exception ex) { session.Log($"[WARN] RemoveAutoStart: {ex.Message}"); return ActionResult.Success; }
        }

        [CustomAction]
        public static ActionResult RevertSecurity(Session session)
        {
            session.Log("=== RevertSecurity: START ===");
            try
            {
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoRun");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableCMD");
                RemoveRegistryPolicy(session, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr");
                session.Log("[OK] Security restrictions reverted");
                return ActionResult.Success;
            }
            catch (Exception ex) { session.Log($"[WARN] RevertSecurity: {ex.Message}"); return ActionResult.Success; }
        }

        private static int RunCommand(string fileName, string arguments, Session session, int timeoutMs = 60000)
        {
            var psi = new ProcessStartInfo
            {
                FileName = fileName, Arguments = arguments,
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true
            };
            using (var process = Process.Start(psi))
            {
                process.BeginErrorReadLine();
                process.ErrorDataReceived += (s, e) => { if (e.Data != null) session.Log($"  [STDERR] {e.Data}"); };
                string stdout = process.StandardOutput.ReadToEnd();
                bool exited = process.WaitForExit(timeoutMs);
                if (!string.IsNullOrWhiteSpace(stdout)) session.Log($"  [STDOUT] {stdout.TrimEnd()}");
                if (!exited) { try { process.Kill(); } catch { } return -1; }
                session.Log($"  [CMD] {fileName} exit={process.ExitCode}");
                return process.ExitCode;
            }
        }

        private static void RemoveRegistryPolicy(Session session, string subKey, string name)
        {
            try
            {
                using (var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64).OpenSubKey(subKey, true))
                { if (key?.GetValue(name) != null) { key.DeleteValue(name); session.Log($"  Removed policy: {name}"); } }
            }
            catch { session.Log($"  Policy not set: {name}"); }
        }
    }
}

