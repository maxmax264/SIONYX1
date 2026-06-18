content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', encoding='utf-8').read()
old = '''    public async Task<FirebaseResult> DbGetAsync(string path)
    {
        if (!await EnsureValidTokenAsync())
            return FirebaseResult.Fail("Not authenticated");'''
new = '''    public async Task<FirebaseResult> DbGetPublicAsync(string path)
    {
        var orgPath = GetOrgPath(path);
        var url = $"{_databaseUrl}/{orgPath}.json";
        try
        {
            var response = await _http.GetAsync(url);
            response.EnsureSuccessStatusCode();
            var json = await response.Content.ReadAsStringAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(json);
            Logger.Debug("DB public read: {Path}", orgPath);
            return FirebaseResult.Ok(data);
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "DB public read failed: {Path}", orgPath);
            return FirebaseResult.Fail(ex.Message);
        }
    }

    public async Task<FirebaseResult> DbGetAsync(string path)
    {
        if (!await EnsureValidTokenAsync())
            return FirebaseResult.Fail("Not authenticated");'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
