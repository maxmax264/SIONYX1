f=open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c=f.read()
f.close()

old='        _ = LoadBackgroundAsync();\n    }'
new='        _ = LoadBackgroundAsync();\n        _ = StartRefreshListenerAsync();\n    }'
assert c.count(old)==1
c=c.replace(old,new,1)

old='    public async Task ReloadBackgroundAsync() => await LoadBackgroundAsync();'
new='''    public async Task ReloadBackgroundAsync() => await LoadBackgroundAsync();

    private async Task StartRefreshListenerAsync()
    {
        if (_metadataService == null) return;
        try
        {
            var config = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
            using var http = new System.Net.Http.HttpClient();
            http.Timeout = System.Threading.Timeout.InfiniteTimeSpan;
            var url = $"{config.DatabaseUrl}/organizations/{config.OrgId}/metadata/kioskRefreshAt.json";
            string? lastVal = null;
            while (true)
            {
                try
                {
                    var json = await http.GetStringAsync(url);
                    var val = json.Trim().Trim('"');
                    if (lastVal != null && val != lastVal)
                    {
                        Serilog.Log.Information("[BG] Refresh triggered from dashboard");
                        await ReloadBackgroundAsync();
                    }
                    lastVal = val;
                }
                catch { }
                await System.Threading.Tasks.Task.Delay(3000);
            }
        }
        catch (Exception ex) { Serilog.Log.Error(ex, "[BG] RefreshListener failed"); }
    }'''
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs','w',encoding='utf-8').write(c)
print("OK")
