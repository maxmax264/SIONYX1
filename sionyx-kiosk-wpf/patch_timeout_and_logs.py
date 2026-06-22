path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

errors = []

# 1. Increase timeout from 90s to 5 minutes
old1 = "WaitForRegistryVersionAsync(version, msiPath, TimeSpan.FromSeconds(90))"
new1 = "WaitForRegistryVersionAsync(version, msiPath, TimeSpan.FromMinutes(5))"
if old1 in content:
    content = content.replace(old1, new1, 1)
    print("Patched: timeout 90s -> 5min")
else:
    errors.append("timeout not found")

# 2. Add detailed log after trigger re-write in poll loop
old2 = '            try { File.WriteAllText(Path.Combine(GetUpdateFolder(), "pending_update.txt"), msiPath); }\n            catch { /* non-fatal */ }\n            var current = Infrastructure.RegistryConfig.ReadValue("Version");'
new2 = '''            try
            {
                var tf = Path.Combine(GetUpdateFolder(), "pending_update.txt");
                File.WriteAllText(tf, msiPath);
                Logger.Information("[Update] Poll #{Attempt}: trigger file re-written to {Path}", attempt, tf);
            }
            catch (Exception tfEx)
            {
                Logger.Warning("[Update] Poll #{Attempt}: could not write trigger file: {Err}", attempt, tfEx.Message);
            }
            var current = Infrastructure.RegistryConfig.ReadValue("Version");'''
if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Patched: detailed trigger log in poll")
else:
    errors.append("poll loop log not found")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
else:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("All patches applied!")
