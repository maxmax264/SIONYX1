import sys

path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('    del ""{triggerFile}""')
if idx == -1:
    print("ERROR: del line not found")
    idx2 = content.find("triggerFile")
    if idx2 != -1:
        print("Context around triggerFile:")
        print(repr(content[idx2-20:idx2+150]))
    sys.exit(1)

print(f"Found at index {idx}")
print("Context:", repr(content[idx:idx+80]))

old = '    del ""{triggerFile}""'
new = '    del ""{triggerFile}""\r\n    timeout /t 3 /nobreak >nul\r\n    start """" ""{appExe}"""'

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
