path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '            attempt++;\n            var current = Infrastructure.RegistryConfig.ReadValue("Version");'
new = '            attempt++;\n            // Re-write trigger file every poll so the scheduled task always\n            // has it, even if a previous run deleted it before msiexec finished.\n            try { File.WriteAllText(Path.Combine(GetUpdateFolder(), "pending_update.txt"), msiPath); }\n            catch { /* non-fatal */ }\n            var current = Infrastructure.RegistryConfig.ReadValue("Version");'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("ERROR: not found")
    idx = content.find("attempt++;")
    print(repr(content[idx-2:idx+100]))
