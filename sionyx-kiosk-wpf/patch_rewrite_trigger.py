path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the call site to pass msiPath
old1 = 'var installed = await WaitForRegistryVersionAsync(version, TimeSpan.FromSeconds(90));'
new1 = 'var installed = await WaitForRegistryVersionAsync(version, msiPath, TimeSpan.FromSeconds(90));'

# 2. Update the signature to accept msiPath
old2 = 'private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, TimeSpan timeout)'
new2 = 'private static async Task<bool> WaitForRegistryVersionAsync(string expectedVersion, string msiPath, TimeSpan timeout)'

# 3. Add trigger re-write inside the poll loop
old3 = '''              attempt++;
              var current = Infrastructure.RegistryConfig.ReadValue("Version");'''
new3 = '''              attempt++;
              // Re-write trigger file every poll so the scheduled task always
              // has it, even if a previous run deleted it before msiexec finished.
              try { File.WriteAllText(Path.Combine(GetUpdateFolder(), "pending_update.txt"), msiPath); }
              catch { /* non-fatal */ }
              var current = Infrastructure.RegistryConfig.ReadValue("Version");'''

errors = []
for old, new, label in [(old1, new1, "call site"), (old2, new2, "signature"), (old3, new3, "poll loop")]:
    if old not in content:
        errors.append(f"NOT FOUND: {label}")
    else:
        content = content.replace(old, new, 1)
        print(f"Patched: {label}")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
else:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("All patches applied successfully!")
