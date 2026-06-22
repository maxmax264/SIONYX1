import sys

path = r"src\SionyxKiosk\Views\Dialogs\SettingsDialog.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = 'var savedInterval = RegistryConfig.ReadValue("UpdateCheckIntervalMinutes") ?? "0";'
new = 'var savedInterval = RegistryConfig.ReadValueCurrentUser("UpdateCheckIntervalMinutes") ?? "0";'

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
