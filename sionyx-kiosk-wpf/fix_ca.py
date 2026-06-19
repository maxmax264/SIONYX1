content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '''        // ====================================================================
        //  UNINSTALL ACTIONS
        // ===================================================================='''
new = '''        [CustomAction]
        public static ActionResult SetupUpdateTask(Session session)
        {
            session.Log("=== SetupUpdateTask: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string triggerFile = Path.Combine(installDir, "pending_update.txt");

                // Create a batch script that reads the MSI path and runs it
                string scriptPath = Path.Combine(installDir, "run_update.bat");
                string scriptContent = $@"@echo off
if exist ""{triggerFile}"" (
    set /p MSI_PATH=<""{triggerFile}""
    msiexec /i ""%MSI_PATH%"" /quiet /norestart
    del ""{triggerFile}""
)";
                File.WriteAllText(scriptPath, scriptContent);
                session.Log($"[OK] Update script created: {scriptPath}");

                // Create scheduled task SIONYX_Update running as SYSTEM
                string taskXml = $@"<?xml version=""1.0"" encoding=""UTF-16""?>
<Task version=""1.2"" xmlns=""http://schemas.microsoft.com/windows/2004/02/mit/task"">
  <Principals>
    <Principal id=""Author"">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context=""Author"">
    <Exec>
      <Command>{scriptPath}</Command>
    </Exec>
  </Actions>
</Task>";

                string xmlPath = Path.Combine(Path.GetTempPath(), "sionyx_update_task.xml");
                File.WriteAllText(xmlPath, taskXml, System.Text.Encoding.Unicode);

                RunCommand("schtasks", $"/create /tn \"SIONYX_Update\" /xml \"{xmlPath}\" /f", session);
                session.Log("[OK] SIONYX_Update scheduled task created");

                try { File.Delete(xmlPath); } catch { }
                return ActionResult.Success;
            }
            catch (Exception ex)
            {
                session.Log($"[WARN] SetupUpdateTask failed: {ex.Message}");
                return ActionResult.Success;
            }
        }

        // ====================================================================
        //  UNINSTALL ACTIONS
        // ===================================================================='''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
