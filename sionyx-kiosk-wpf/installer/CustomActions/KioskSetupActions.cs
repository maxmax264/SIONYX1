using System;
using System.Diagnostics;
using System.IO;
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

        // ====================================================================
        //  INSTALL ACTIONS
        // ====================================================================

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
                    if (runKey == null)
                    {
                        session.Log("[ERROR] Could not open HKLM Run key");
                        return ActionResult.Failure;
                    }
                    runKey.SetValue(RunValueName, runValue, RegistryValueKind.String);
                    session.Log($"[OK] HKLM Run set: {runValue}");
                }

                session.Log($"=== SetupAutoStart: DONE ({sw.ElapsedMilliseconds}ms) ===");
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] SetupAutoStart failed: {ex}");
                return ActionResult.Failure;
            }
        }

        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            session.Log("=== LaunchKiosk: START ===");
            try
            {
                // In immediate mode, read directly from session properties
                string installDir = session["INSTALLFOLDER"] ?? session.CustomActionData["INSTALLDIR"] ?? @"C:\Program Files\SIONYX";
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

                // 1. Exe
                string exePath = Path.Combine(installDir, "SionyxKiosk.exe");
                if (File.Exists(exePath))
                    Log($"[PASS] Exe exists: {exePath}");
                else
                {
                    Log($"[FAIL] Exe missing: {exePath}");
                    errors.Add("Application executable was not installed");
                }

                // 2. Registry SIONYX keys
                string[] regKeys = { "Install_Dir", "Version", "OrgId", "FirebaseProjectId" };
                using (var appKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                               .OpenSubKey($@"SOFTWARE\{AppName}"))
                {
                    var missing = new System.Collections.Generic.List<string>();
                    foreach (var k in regKeys)
                        if (appKey?.GetValue(k) == null) missing.Add(k);
                    if (missing.Count == 0)
                        Log("[PASS] Registry keys OK");
                    else
                    {
                        Log($"[FAIL] Missing registry keys: {string.Join(", ", missing)}");
                        errors.Add($"Missing registry keys: {string.Join(", ", missing)}");
                    }
                }

                // 3. HKLM Run
                using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var runKey = baseKey.OpenSubKey(RunKeyPath))
                {
                    var val = runKey?.GetValue(RunValueName) as string;
                    if (!string.IsNullOrEmpty(val))
                        Log($"[PASS] HKLM Run entry exists: {val}");
                    else
                    {
                        Log("[FAIL] HKLM Run entry missing");
                        errors.Add("Auto-start registry entry not found");
                    }
                }

                Log(errors.Count == 0
                    ? "[OK] ALL CHECKS PASSED"
                    : $"[ERROR] {errors.Count} check(s) failed: {string.Join("; ", errors)}");

                try { File.WriteAllText(Path.Combine(installDir, "install.log"), log.ToString()); }
                catch { }

                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[ERROR] VerifyInstallation failed: {ex}");
                return ActionResult.Success;
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
        public static ActionResult RemoveAutoStart(Session session)
        {
            session.Log("=== RemoveAutoStart: START ===");
            try
            {
                using (var baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var runKey = baseKey.OpenSubKey(RunKeyPath, true))
                {
                    if (runKey?.GetValue(RunValueName) != null)
                    {
                        runKey.DeleteValue(RunValueName, false);
                        session.Log("[OK] HKLM Run entry removed");
                    }
                    else
                        session.Log("[INFO] HKLM Run entry not found");
                }
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] RemoveAutoStart: {ex.Message}");
                return ActionResult.Success;
            }
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
            catch (Exception ex)
            {
                session.Log($"[WARN] RevertSecurity: {ex.Message}");
                return ActionResult.Success;
            }
        }

        // ====================================================================
        //  HELPERS
        // ====================================================================

        private static int RunCommand(string fileName, string arguments, Session session, int timeoutMs = 60000)
        {
            var psi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
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
            catch { session.Log($"  Policy not set: {name}"); }
        }
    }
}
