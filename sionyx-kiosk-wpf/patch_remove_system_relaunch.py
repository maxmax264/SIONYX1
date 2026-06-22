path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# The exact bat script content is built as a C# interpolated string inside
# SetupUpdateTask(). We look for the "start" line that launches the kiosk
# exe and remove it (and the timeout right before it, which existed only to
# give the exe time to release file locks before that start command ran).
old_bat_tail = '''    del ""{triggerFile}""
    timeout /t 3 /nobreak >nul
    start "" ""{appExe}""
)"'''

new_bat_tail = '''    del ""{triggerFile}""
)
REM NOTE: the kiosk exe is intentionally NOT relaunched here. This script
REM runs as SYSTEM (via the SIONYX_Update scheduled task), and launching the
REM exe from a SYSTEM context creates a second, non-interactive instance
REM that runs alongside the real user's kiosk and reads the wrong (SYSTEM)
REM registry hive for settings. The kiosk process itself (running as the
REM interactive user) polls the registry after writing the trigger file and
REM relaunches itself once it confirms the new version was installed."'''

count = content.count(old_bat_tail)
if count == 1:
    content = content.replace(old_bat_tail, new_bat_tail)
    changes += 1
    print("Applied: removed kiosk relaunch from run_update.bat template.")
else:
    print(f"NOT applied: found {count} occurrences of expected bat tail, expected 1.")
    print("Will try an alternate, looser match next.")

    # Looser fallback: just remove the specific start line, keep everything else.
    old_start_line = '    start "" ""{appExe}""\\n'
    if old_start_line in content:
        content = content.replace(old_start_line, '')
        changes += 1
        print("Applied (fallback): removed just the start line.")
    else:
        # Try without escaped quotes variant
        old_start_line2 = 'start "" ""{appExe}""'
        if old_start_line2 in content:
            content = content.replace(old_start_line2, 'rem kiosk relaunch removed - handled by InstallAsync polling instead')
            changes += 1
            print("Applied (fallback 2): replaced start line with comment.")
        else:
            print("ERROR: could not find the start line in any expected form.")
            print("Please paste the SetupUpdateTask method content so the patch can be made exact.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal changes applied: {changes}.")
