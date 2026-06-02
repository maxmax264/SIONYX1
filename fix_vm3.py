content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''    /// <summary>Called by App when auto-login succeeds.</summary>
    public void TriggerAutoLogin() => LoginSucceeded?.Invoke();
}'''

new = '''    private async Task LoadAuthDesignAsync()
    {
        try
        {
            var cfg = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
            using var http = new System.Net.Http.HttpClient();
            var url = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/authDesign.json";
            var json = await http.GetStringAsync(url);
            if (json == "null" || string.IsNullOrEmpty(json)) return;
            var d = System.Text.Json.JsonDocument.Parse(json).RootElement;
            System.Windows.Application.Current.Dispatcher.Invoke(() =>
            {
                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = c1.GetString() ?? "#6366F1";
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = c2.GetString() ?? "#8B5CF6";
                if (d.TryGetProperty("brandSubtitle", out var bs)) BrandSubtitle = bs.GetString() ?? "";
                if (d.TryGetProperty("welcomeText", out var wt)) WelcomeText = wt.GetString() ?? "";
                if (d.TryGetProperty("welcomeSubtext", out var ws)) WelcomeSubtext = ws.GetString() ?? "";
                if (d.TryGetProperty("showRegister", out var sr)) ShowRegister = sr.GetBoolean();
                if (d.TryGetProperty("cleanMode", out var cm)) CleanMode = cm.GetBoolean();

                // עדכן את הגרדיאנט
                try
                {
                    var col1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor1);
                    var col2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor2);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(col1, col2, 45);
                }
                catch { }
            });
            Serilog.Log.Information("[Design] authDesign loaded OK");
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[Design] Failed to load authDesign"); }
    }

    /// <summary>Called by App when auto-login succeeds.</summary>
    public void TriggerAutoLogin() => LoginSucceeded?.Invoke();
}'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
