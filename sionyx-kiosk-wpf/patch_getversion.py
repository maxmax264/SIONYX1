import sys

path = r"src\SionyxKiosk\App.xaml.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''    private static string GetVersion()
    {
        try
        {
            var path = Path.Combine(AppContext.BaseDirectory, "version.json");
            if (!File.Exists(path)) return "1.0.0";
            var json = File.ReadAllText(path);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            if (root.TryGetProperty("version", out var ver) && ver.ValueKind == JsonValueKind.String)
                return ver.GetString() ?? "1.0.0";
        }
        catch (Exception ex)
        {
            Log.Warning(ex, "Could not read version.json, using fallback");
        }
        return "1.0.0";
    }'''

new = '''    private static string GetVersion()
    {
        // First try Registry (production installs write version here)
        try
        {
            var regVersion = Infrastructure.RegistryConfig.ReadValue("Version");
            if (!string.IsNullOrWhiteSpace(regVersion)) return regVersion;
        }
        catch { }

        // Fallback: version.json (development builds)
        try
        {
            var path = Path.Combine(AppContext.BaseDirectory, "version.json");
            if (File.Exists(path))
            {
                var json = File.ReadAllText(path);
                using var doc = JsonDocument.Parse(json);
                var root = doc.RootElement;
                if (root.TryGetProperty("version", out var ver) && ver.ValueKind == JsonValueKind.String)
                    return ver.GetString() ?? "1.0.0";
            }
        }
        catch (Exception ex)
        {
            Log.Warning(ex, "Could not read version.json, using fallback");
        }
        return "1.0.0";
    }'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
