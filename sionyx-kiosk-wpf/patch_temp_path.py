import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = 'var tempPath = Path.Combine(AppContext.BaseDirectory, $"sionyx_update_{newVersion}.msi");'
new = 'var tempPath = Path.Combine(Path.GetTempPath(), $"sionyx_update_{newVersion}.msi");'

count = content.count(old)
if count == 0:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new)
print(f"Replaced {count} occurrence(s)")

# Also fix the trigger file path
old2 = 'var triggerFile = Path.Combine(AppContext.BaseDirectory, "pending_update.txt");'
new2 = 'var triggerFile = Path.Combine(Path.GetTempPath(), "pending_update.txt");'

if old2 in content:
    content = content.replace(old2, new2)
    print("Also fixed triggerFile path")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
