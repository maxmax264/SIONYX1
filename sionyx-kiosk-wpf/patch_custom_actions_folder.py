path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = r'Path.Combine(@"C:\Windows\Temp", "pending_update.txt")'
new = r'Path.Combine(@"C:\Users\Public\Documents\SIONYX\updates", "pending_update.txt")'

count = content.count(old)
if count == 0:
    print("ERROR: triggerFile pattern not found in KioskSetupActions.cs")
elif count > 1:
    print(f"ERROR: triggerFile pattern found {count} times, expected 1")
else:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched KioskSetupActions.cs successfully!")
    print("NOTE: this only takes effect on the NEXT installer build (.msi),")
    print("since CustomActions.dll is compiled into the installer itself.")
