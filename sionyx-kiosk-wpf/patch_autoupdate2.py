import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add static events after class opening
old = '    public static string? PendingUpdateVersion => _pendingUpdateVersion;'
new = '''    // Progress events — UI subscribes to these
    public static event Action<string>? UpdateStarted;   // version
    public static event Action<int, string>? ProgressChanged; // percent, status
    public static event Action? UpdateCompleted;

    public static string? PendingUpdateVersion => _pendingUpdateVersion;'''

content = content.replace(old, new, 1)

# Replace DownloadAndInstallAsync with progress reporting
old2 = '''    private static async Task DownloadAndInstallAsync(string downloadUrl, string newVersion, string currentVersion)
    {
        try
        {
            var tempPath = Path.Combine(AppContext.BaseDirectory, $"sionyx_update_{newVersion}.msi");
            Logger.Information("[Update] Downloading {Url}", downloadUrl);
            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromMinutes(10);
            var bytes = await http.GetByteArrayAsync(downloadUrl);
            await File.WriteAllBytesAsync(tempPath, bytes);
            Logger.Information("[Update] Download complete ({MB} MB)", bytes.Length / 1024 / 1024);
            await InstallAsync(tempPath, newVersion);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Download+install failed");
        }
    }'''

new2 = '''    private static async Task DownloadAndInstallAsync(string downloadUrl, string newVersion, string currentVersion)
    {
        try
        {
            UpdateStarted?.Invoke(newVersion);
            ProgressChanged?.Invoke(0, "מתחיל הורדה...");

            var tempPath = Path.Combine(AppContext.BaseDirectory, $"sionyx_update_{newVersion}.msi");
            Logger.Information("[Update] Downloading {Url}", downloadUrl);

            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromMinutes(10);

            using var response = await http.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);
            var totalBytes = response.Content.Headers.ContentLength ?? 0;
            var buffer = new byte[81920];
            var downloaded = 0L;

            await using var stream = await response.Content.ReadAsStreamAsync();
            await using var fileStream = File.Create(tempPath);

            int read;
            while ((read = await stream.ReadAsync(buffer)) > 0)
            {
                await fileStream.WriteAsync(buffer.AsMemory(0, read));
                downloaded += read;
                if (totalBytes > 0)
                {
                    var percent = (int)(downloaded * 100 / totalBytes);
                    var mb = downloaded / 1024.0 / 1024.0;
                    var totalMb = totalBytes / 1024.0 / 1024.0;
                    ProgressChanged?.Invoke(percent, $"מוריד... {mb:F1} / {totalMb:F1} MB");
                }
            }

            Logger.Information("[Update] Download complete ({MB} MB)", downloaded / 1024 / 1024);
            ProgressChanged?.Invoke(90, "מתקין עדכון...");
            await InstallAsync(tempPath, newVersion);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Download+install failed");
        }
    }'''

content = content.replace(old2, new2, 1)

# Add UpdateCompleted event before shutdown
old3 = '''            Logger.Information("[Update] Install complete — restarting kiosk");

            await Task.Delay(3000);'''
new3 = '''            Logger.Information("[Update] Install complete — restarting kiosk");

            UpdateCompleted?.Invoke();
            await Task.Delay(3000);'''

content = content.replace(old3, new3, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
