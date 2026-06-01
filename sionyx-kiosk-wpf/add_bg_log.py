f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = '''    private async Task LoadBackgroundAsync()
    {
        if (_metadataService == null) return;
        try
        {
            var result = await _metadataService.GetKioskBackgroundAsync();
            if (result.IsSuccess && result.Data is { } data)
            {
                var type = data.GetType();
                var enabled = type.GetProperty("enabled")?.GetValue(data) is bool b && b;
                var url = type.GetProperty("url")?.GetValue(data)?.ToString() ?? "";
                if (enabled && !string.IsNullOrWhiteSpace(url))
                {
                    BackgroundImageUrl = url;
                    HasBackgroundImage = true;
                    return;
                }
            }
        }
        catch { }
        BackgroundImageUrl = "";
        HasBackgroundImage = false;
    }'''

new = '''    private async Task LoadBackgroundAsync()
    {
        if (_metadataService == null) { Serilog.Log.Warning("[BG] metadataService is null"); return; }
        try
        {
            var result = await _metadataService.GetKioskBackgroundAsync();
            Serilog.Log.Information("[BG] IsSuccess={S} dataType={D}", result.IsSuccess, result.Data?.GetType().Name ?? "null");
            if (result.IsSuccess && result.Data is { } data)
            {
                var type = data.GetType();
                var enabled = type.GetProperty("enabled")?.GetValue(data) is bool b && b;
                var url = type.GetProperty("url")?.GetValue(data)?.ToString() ?? "";
                Serilog.Log.Information("[BG] enabled={E} urlLen={L}", enabled, url.Length);
                if (enabled && !string.IsNullOrWhiteSpace(url))
                {
                    BackgroundImageUrl = url;
                    HasBackgroundImage = true;
                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);
                    return;
                }
            }
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[BG] Exception loading background"); }
        BackgroundImageUrl = "";
        HasBackgroundImage = false;
        Serilog.Log.Warning("[BG] No background set");
    }'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
print("OK")
