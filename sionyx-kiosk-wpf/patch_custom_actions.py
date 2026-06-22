import sys

path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string triggerFile = Path.Combine(installDir, "pending_update.txt");

                // Create a batch script that reads the MSI path and runs it
                string scriptPath = Path.Combine(installDir, "run_update.bat");
                string scriptContent = $@"@echo off
if exist ""{triggerFile}"" (
    set /p MSI_PATH=<""{triggerFile}""
    msiexec /i ""%MSI_PATH%"" /quiet /norestart
    del ""{triggerFile}""
)";'''

new = '''                string installDir = session.CustomActionData["INSTALLDIR"];
                string appExe = Path.Combine(installDir, "SionyxKiosk.exe");
                string tempDir = Path.GetTempPath();
                string triggerFile = Path.Combine(tempDir, "pending_update.txt");

                // Create a batch script that reads the MSI path and runs it
                string scriptPath = Path.Combine(installDir, "run_update.bat");
                string scriptContent = $@"@echo off
if exist ""{triggerFile}"" (
    set /p MSI_PATH=<""{triggerFile}""
    taskkill /f /im SionyxKiosk.exe 2>nul
    timeout /t 2 /nobreak >nul
    msiexec /i ""%MSI_PATH%"" /quiet /norestart
    del ""{triggerFile}""
    timeout /t 3 /nobreak >nul
    start """" ""{appExe}""
)";'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
