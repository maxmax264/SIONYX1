import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = 'var raw = Infrastructure.RegistryConfig.ReadValue("UpdateCheckIntervalMinutes");'
new = 'var raw = Infrastructure.RegistryConfig.ReadValueCurrentUser("UpdateCheckIntervalMinutes");'

if old not in content:
    print("ERROR: Target line not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
