path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''    del ""{triggerFile}""
    timeout /t 3 /nobreak >nul
    start """" ""{appExe}""
)";'''

new = '''    del ""{triggerFile}""
)
REM The kiosk exe is intentionally NOT relaunched here. This script runs as
REM SYSTEM via the SIONYX_Update scheduled task. Launching the exe from a
REM SYSTEM context creates a second, non-interactive instance running
REM alongside the real user's kiosk (and reading the wrong, SYSTEM registry
REM hive for settings). The kiosk process itself polls the registry after
REM writing the trigger file and relaunches itself as the interactive user
REM once it confirms the new version was installed (see InstallAsync /
REM WaitForRegistryVersionAsync in AutoUpdateService.cs).
";'''

count = content.count(old)
if count == 0:
    print("ERROR: pattern not found.")
elif count > 1:
    print(f"ERROR: pattern found {count} times, expected 1.")
else:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched successfully! run_update.bat will no longer relaunch the kiosk as SYSTEM.")
    print("NOTE: appExe variable is now unused in SetupUpdateTask except for the comment text - that's fine, it's still referenced in scriptContent's removed line context but no longer interpolated there.")
