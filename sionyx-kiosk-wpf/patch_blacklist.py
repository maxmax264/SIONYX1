import sys

path = r"src\SionyxKiosk\Services\ProcessRestrictionService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '        "teamviewer.exe", "anydesk.exe", "ultraviewer.exe",\n        "SystemSettings.exe",'
new = '        "systemsettings.exe",\n        "teamviewer.exe", "anydesk.exe", "ultraviewer.exe",'

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
