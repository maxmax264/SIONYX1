path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    # DownloadInBackgroundAsync - tempPath
    (r'Path.Combine(@"C:\\Windows\\Temp", $"sionyx_update_{version}.msi")',
     r'Path.Combine(GetUpdateFolder(), $"sionyx_update_{version}.msi")'),
    # DownloadAndInstallAsync - tempPath
    (r'Path.Combine(@"C:\Windows\Temp", $"sionyx_update_{newVersion}.msi")',
     r'Path.Combine(GetUpdateFolder(), $"sionyx_update_{newVersion}.msi")'),
    # TryRunViaScheduledTask - triggerFile
    (r'Path.Combine(@"C:\Windows\Temp", "pending_update.txt")',
     r'Path.Combine(GetUpdateFolder(), "pending_update.txt")'),
]

applied = 0
for old, new in replacements:
    count = content.count(old)
    if count == 1:
        content = content.replace(old, new)
        applied += 1
    elif count == 0:
        print(f"WARNING: pattern not found: {old}")
    else:
        print(f"WARNING: pattern found {count} times (expected 1): {old}")

# Add the GetUpdateFolder helper method right before the closing brace of the class.
# We insert it right after the IsNewerVersion method, which is the last method in the class.
anchor = '''    private static bool IsNewerVersion(string latest, string current)
    {
        try { return Version.Parse(latest) > Version.Parse(current); }
        catch { return string.Compare(latest, current, StringComparison.Ordinal) > 0; }
    }
}'''

new_anchor = '''    private static bool IsNewerVersion(string latest, string current)
    {
        try { return Version.Parse(latest) > Version.Parse(current); }
        catch { return string.Compare(latest, current, StringComparison.Ordinal) > 0; }
    }

    /// <summary>
    /// Returns a writable folder for staging the downloaded MSI and the
    /// trigger file that the SYSTEM scheduled task reads. C:\\Windows\\Temp
    /// was tried first but some machines have non-standard ACLs on it that
    /// silently truncate writes for regular (non-admin) users. This folder
    /// (under Public Documents) grants Modify to INTERACTIVE users and Full
    /// Control to SYSTEM by default on every Windows install, so it is safe
    /// across machines without any manual ACL changes.
    /// </summary>
    private static string GetUpdateFolder()
    {
        var folder = Path.Combine(@"C:\\Users\\Public\\Documents\\SIONYX", "updates");
        Directory.CreateDirectory(folder);
        return folder;
    }
}'''

if anchor in content:
    content = content.replace(anchor, new_anchor)
    applied += 1
else:
    print("WARNING: anchor for GetUpdateFolder insertion not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {applied} of 4 expected changes.")
