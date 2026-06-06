content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', encoding='utf-8').read()
old = '''    /// <summary>Close browsers first, then clean up. Recommended for session end.</summary>
    public Dictionary<string, object> CleanupWithBrowserClose()
    {
        Logger.Information("Closing browsers before cleanup...");

        var closeResults = CloseBrowsers();
        Thread.Sleep(1000); // Let browsers finish closing

        var results = CleanupAllBrowsers();
        results["browsers_closed"] = closeResults;
        return results;
    }'''
new = '''    /// <summary>Close browsers first, then clean up. Recommended for session end.</summary>
    public Dictionary<string, object> CleanupWithBrowserClose()
    {
        Logger.Information("=== BROWSER CLEANUP STARTED ===");

        var closeResults = CloseBrowsers();
        Logger.Information("Browsers closed: {Results}", string.Join(", ", closeResults.Select(kv => $"{kv.Key}={kv.Value}")));
        Thread.Sleep(1500); // Let browsers finish closing

        var results = CleanupAllBrowsers();
        results["browsers_closed"] = closeResults;

        Logger.Information("=== BROWSER CLEANUP FINISHED ===");
        return results;
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
