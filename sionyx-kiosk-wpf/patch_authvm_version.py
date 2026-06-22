import sys

path = r"src\SionyxKiosk\ViewModels\AuthViewModel.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''    public string AppVersion => $"v{ReadVersion()}";
    private static string ReadVersion()
    {
        try
        {
            var p = System.IO.Path.Combine(AppContext.BaseDirectory, "version.json");
            if (!System.IO.File.Exists(p)) return "1.0.0";
            var json = System.IO.File.ReadAllText(p);
            using var doc = System.Text.Json.JsonDocument.Parse(json);
            if (doc.RootElement.TryGetProperty("version", out var v)) return v.GetString() ?? "1.0.0";
        }
        catch { }
        return "1.0.0";
    }'''

new = '''    public string AppVersion => $"v{ReadVersion()}";
    private static string ReadVersion()
    {
        // First try Registry (production)
        try
        {
            var reg = SionyxKiosk.Infrastructure.RegistryConfig.ReadValue("Version");
            if (!string.IsNullOrWhiteSpace(reg)) return reg;
        }
        catch { }

        // Fallback: version.json (development)
        try
        {
            var p = System.IO.Path.Combine(AppContext.BaseDirectory, "version.json");
            if (System.IO.File.Exists(p))
            {
                var json = System.IO.File.ReadAllText(p);
                using var doc = System.Text.Json.JsonDocument.Parse(json);
                if (doc.RootElement.TryGetProperty("version", out var v)) return v.GetString() ?? "1.0.0";
            }
        }
        catch { }
        return "1.0.0";
    }'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
