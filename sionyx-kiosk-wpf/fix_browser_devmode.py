content = open(r'.\src\SionyxKiosk\Services\BrowserCleanupService.cs', encoding='utf-8').read()

old = '''using System.Diagnostics;
using System.IO;
using Serilog;

namespace SionyxKiosk.Services;'''

new = '''using System.Diagnostics;
using System.IO;
using Microsoft.Win32;
using Serilog;

namespace SionyxKiosk.Services;'''

count = content.count(old)
print(f"Found {count} matches for import fix")
if count == 1:
    content = content.replace(old, new, 1)
    print("Import fix OK")
else:
    print("NOT FOUND - import")

old2 = '''    /// <summary>Delete all files in SionyxUser Downloads folder.</summary>
    public void CleanupDownloads()'''

new2 = '''    /// <summary>Returns true if running in dev/test mode — skips destructive cleanup.</summary>
    private static bool IsDevMode()
    {
        var envVar = Environment.GetEnvironmentVariable("SIONYX_DEV_MODE");
        if (envVar == "1" || string.Equals(envVar, "true", StringComparison.OrdinalIgnoreCase))
            return true;
        try
        {
            using var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                       .OpenSubKey(@"SOFTWARE\SIONYX");
            if (key?.GetValue("DevMode") is int val && val == 1)
                return true;
        }
        catch { }
        return false;
    }

    /// <summary>Delete all files in user Downloads folder.</summary>
    public void CleanupDownloads()'''

count2 = content.count(old2)
print(f"Found {count2} matches for DevMode insert")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("DevMode insert OK")
else:
    print("NOT FOUND - DevMode insert")

old3 = '''    /// <summary>Close browsers first, then clean up. Recommended for session end.</summary>
    public Dictionary<string, object> CleanupWithBrowserClose()
    {
        Logger.Information("=== BROWSER CLEANUP STARTED ===");'''

new3 = '''    /// <summary>Close browsers first, then clean up. Recommended for session end.</summary>
    public Dictionary<string, object> CleanupWithBrowserClose()
    {
        if (IsDevMode())
        {
            Logger.Information("=== BROWSER CLEANUP SKIPPED (DevMode) ===");
            return new Dictionary<string, object> { ["success"] = true, ["skipped"] = true };
        }
        Logger.Information("=== BROWSER CLEANUP STARTED ===");'''

count3 = content.count(old3)
print(f"Found {count3} matches for CleanupWithBrowserClose guard")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("CleanupWithBrowserClose guard OK")
else:
    print("NOT FOUND - CleanupWithBrowserClose guard")

old4 = '''    /// <summary>Delete all files in user Downloads folder.</summary>
    public void CleanupDownloads()
    {
        var downloadsPath = Path.Combine(@"C:\\Users\\SionyxUser\\Downloads");'''

new4 = '''    /// <summary>Delete all files in user Downloads folder.</summary>
    public void CleanupDownloads()
    {
        if (IsDevMode())
        {
            Logger.Information("Downloads cleanup skipped (DevMode)");
            return;
        }
        var downloadsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");'''

count4 = content.count(old4)
print(f"Found {count4} matches for Downloads path fix")
if count4 == 1:
    content = content.replace(old4, new4, 1)
    print("Downloads path fix OK")
else:
    print("NOT FOUND - Downloads path fix")

open(r'.\src\SionyxKiosk\Services\BrowserCleanupService.cs', 'w', encoding='utf-8').write(content)
print("DONE")
