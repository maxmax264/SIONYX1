import sys, re

path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the scriptContent and add safety-net relaunch after msiexec
old = '''string scriptContent = $@"@echo off
if exist ""{triggerFile}"" (
    set /p MSI_PATH=<""{triggerFile}""
    taskkill /f /im SionyxKiosk.exe 2>nul
    timeout /t 2 /nobreak >nul
    msiexec /i ""%MSI_PATH%"" /quiet /norestart
    del ""{triggerFile}""
)";'''

new = '''string scriptContent = $@"@echo off
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

print("Patched successfully! Safety-net relaunch added to run_update.bat.")
