import sys

path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '                string tempDir = Path.GetTempPath();\n                string triggerFile = Path.Combine(tempDir, "pending_update.txt");'
new = '                string triggerFile = Path.Combine(@"C:\\Windows\\Temp", "pending_update.txt");'

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
