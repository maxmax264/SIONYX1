content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', encoding='utf-8').read()
old = '''    private Dictionary<string, object> CleanupChromiumBrowser(string browserName, string[] basePaths)
    {
        var filesDeleted = 0;
        var errors = new List<string>();

        foreach (var basePath in basePaths)
        {
            if (!Directory.Exists(basePath)) continue;

            var profiles = FindChromiumProfiles(basePath);
            foreach (var profile in profiles)
            {
                foreach (var fileName in ChromiumFiles)
                {
                    var filePath = Path.Combine(profile, fileName);
                    filesDeleted += TryDeleteFileOrDir(filePath, browserName, errors);
                }
            }
        }

        Logger.Information("{Browser}: Cleanup complete, {Count} files deleted", browserName, filesDeleted);
        return new Dictionary<string, object>
        {
            ["success"] = errors.Count == 0,
            ["files_deleted"] = filesDeleted,
        };
    }'''
new = '''    private Dictionary<string, object> CleanupChromiumBrowser(string browserName, string[] basePaths)
    {
        var filesDeleted = 0;
        var errors = new List<string>();

        foreach (var basePath in basePaths)
        {
            if (!Directory.Exists(basePath)) continue;

            var profiles = FindChromiumProfiles(basePath);
            foreach (var profile in profiles)
            {
                filesDeleted += TryDeleteFileOrDir(profile, browserName, errors);
                Logger.Information("{Browser}: Deleted profile directory {Profile}", browserName, profile);
            }
        }

        Logger.Information("{Browser}: Cleanup complete, {Count} profiles deleted", browserName, filesDeleted);
        return new Dictionary<string, object>
        {
            ["success"] = errors.Count == 0,
            ["files_deleted"] = filesDeleted,
        };
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
