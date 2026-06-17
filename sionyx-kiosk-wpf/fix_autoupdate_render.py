content = open(r'.\src\SionyxKiosk\Services\AutoUpdateService.cs', encoding='utf-8').read()

old = '    private const string GitHubApiUrl = "https://api.github.com/repos/maxmax264/SIONYX1/releases/latest";\n    private const string AssetPrefix = "sionyx-installer-";'

new = '    private const string UpdateServerUrl = "https://sionyx-auth-server.onrender.com/latest-version";'

count = content.count(old)
print(f"Fix 1: {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix 1 OK")
else:
    print("Fix 1 NOT FOUND")

old2 = '''            var json = await http.GetStringAsync(GitHubApiUrl);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var latestTag = root.GetProperty("tag_name").GetString() ?? "";
            var latestVersion = latestTag.TrimStart('v');

            Logger.Information("[Update] Latest version: {Latest}", latestVersion);

            if (!IsNewerVersion(latestVersion, currentVersion))
            {
                Logger.Information("[Update] Already up to date");
                return;
            }

            Logger.Information("[Update] New version available: {Latest} (current: {Current})", latestVersion, currentVersion);

            // Find MSI asset
            string? downloadUrl = null;
            if (root.TryGetProperty("assets", out var assets))
            {
                foreach (var asset in assets.EnumerateArray())
                {
                    var name = asset.GetProperty("name").GetString() ?? "";
                    if (name.StartsWith(AssetPrefix) && name.EndsWith(".msi"))
                    {
                        downloadUrl = asset.GetProperty("browser_download_url").GetString();
                        break;
                    }
                }
            }

            if (string.IsNullOrEmpty(downloadUrl))
            {
                Logger.Warning("[Update] No MSI asset found in release");
                return;
            }'''

new2 = '''            var json = await http.GetStringAsync(UpdateServerUrl);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var latestVersion = root.GetProperty("version").GetString() ?? "";
            var downloadUrl = root.GetProperty("downloadUrl").GetString() ?? "";

            if (string.IsNullOrEmpty(latestVersion) || string.IsNullOrEmpty(downloadUrl))
            {
                Logger.Information("[Update] No update info available");
                return;
            }

            Logger.Information("[Update] Latest version: {Latest}", latestVersion);

            if (!IsNewerVersion(latestVersion, currentVersion))
            {
                Logger.Information("[Update] Already up to date");
                return;
            }

            Logger.Information("[Update] New version available: {Latest} (current: {Current})", latestVersion, currentVersion);'''

count2 = content.count(old2)
print(f"Fix 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix 2 OK")
else:
    print("Fix 2 NOT FOUND")

open(r'.\src\SionyxKiosk\Services\AutoUpdateService.cs', 'w', encoding='utf-8').write(content)
print("DONE")
