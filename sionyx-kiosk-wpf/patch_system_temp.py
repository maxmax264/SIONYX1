import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = 'var triggerFile = Path.Combine(Path.GetTempPath(), "pending_update.txt");'
new = 'var triggerFile = Path.Combine(@"C:\\Windows\\Temp", "pending_update.txt");'

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

# Also fix the MSI path to use C:\Windows\Temp
old2 = 'var tempPath = Path.Combine(Path.GetTempPath(), $"sionyx_update_{newVersion}.msi");'
new2 = 'var tempPath = Path.Combine(@"C:\\Windows\\Temp", $"sionyx_update_{newVersion}.msi");'

if old2 in content:
    content = content.replace(old2, new2)
    print("Also fixed MSI path")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
