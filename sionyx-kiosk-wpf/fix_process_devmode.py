content = open(r'.\src\SionyxKiosk\Services\ProcessCleanupService.cs', encoding='utf-8').read()

old = '''    /// <summary>Close all user processes that aren\'t in the whitelist.</summary>
    public Dictionary<string, object> CleanupUserProcesses()
    {
        Logger.Information("Starting user process cleanup for new session");'''

new = '''    /// <summary>Returns true if running in dev/test mode — skips destructive cleanup.</summary>
    private static bool IsDevMode()
    {
        var envVar = Environment.GetEnvironmentVariable("SIONYX_DEV_MODE");
        if (envVar == "1" || string.Equals(envVar, "true", StringComparison.OrdinalIgnoreCase))
            return true;
        try
        {
            using var key = Microsoft.Win32.RegistryKey.OpenBaseKey(
                Microsoft.Win32.RegistryHive.LocalMachine,
                Microsoft.Win32.RegistryView.Registry64).OpenSubKey(@"SOFTWARE\SIONYX");
            if (key?.GetValue("DevMode") is int val && val == 1)
                return true;
        }
        catch { }
        return false;
    }

    /// <summary>Close all user processes that aren\'t in the whitelist.</summary>
    public Dictionary<string, object> CleanupUserProcesses()
    {
        if (IsDevMode())
        {
            Logger.Information("Process cleanup skipped (DevMode)");
            return new Dictionary<string, object> { ["success"] = true, ["skipped"] = true };
        }
        Logger.Information("Starting user process cleanup for new session");'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ProcessCleanupService.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
