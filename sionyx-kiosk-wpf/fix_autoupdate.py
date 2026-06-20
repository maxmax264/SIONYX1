content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\AutoUpdateService.cs', encoding='utf-8').read()
old = '    /// <summary>Called by SessionCoordinator after session ends.</summary>\n    public static async Task TryInstallPendingUpdateAsync()'
new = '''    /// <summary>Check now and return result without installing.</summary>
    public static async Task<(bool hasUpdate, string latestVersion, string downloadUrl)> CheckForUpdateNowAsync(string currentVersion)
    {
        try
        {
            using var http = new HttpClient();
            http.DefaultRequestHeaders.Add("User-Agent", "SIONYX-Kiosk");
            http.Timeout = TimeSpan.FromSeconds(10);
            var json = await http.GetStringAsync(UpdateServerUrl);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            var latestVersion = root.GetProperty("version").GetString() ?? "";
            var downloadUrl = root.GetProperty("downloadUrl").GetString() ?? "";
            if (string.IsNullOrEmpty(latestVersion) || string.IsNullOrEmpty(downloadUrl))
                return (false, "", "");
            var hasUpdate = IsNewerVersion(latestVersion, currentVersion);
            return (hasUpdate, latestVersion, downloadUrl);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] CheckForUpdateNow failed");
            return (false, "", "");
        }
    }

    /// <summary>Force download and install immediately (called from tray menu).</summary>
    public static async Task ForceUpdateNowAsync(string currentVersion, Action<string>? statusCallback = null)
    {
        try
        {
            statusCallback?.Invoke("בודק עדכון...");
            var (hasUpdate, latestVersion, downloadUrl) = await CheckForUpdateNowAsync(currentVersion);
            if (!hasUpdate)
            {
                statusCallback?.Invoke("מעודכן לגרסה האחרונה");
                return;
            }
            statusCallback?.Invoke($"מוריד גרסה {latestVersion}...");
            await DownloadAndInstallAsync(downloadUrl, latestVersion, currentVersion);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "[Update] ForceUpdateNow failed");
            statusCallback?.Invoke("שגיאה בעדכון");
        }
    }

    /// <summary>Called by SessionCoordinator after session ends.</summary>
    public static async Task TryInstallPendingUpdateAsync()'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\AutoUpdateService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
