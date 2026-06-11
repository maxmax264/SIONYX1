content = open(r'.\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', encoding='utf-8').read()
old = '    public async Task<FirebaseResult> DbGetAsync(string path)'
new = '''    public async Task<FirebaseResult> DbPushAsync(string path, object data)
    {
        if (!await EnsureValidTokenAsync())
            return FirebaseResult.Fail("Not authenticated");

        var url = $"{_databaseUrl}/{path}.json?auth={_idToken}";
        var json = JsonSerializer.Serialize(data, JsonOptions);
        var response = await _http.PostAsync(url, new StringContent(json, System.Text.Encoding.UTF8, "application/json"));
        if (!response.IsSuccessStatusCode)
            return FirebaseResult.Fail($"Push failed: {response.StatusCode}");

        return FirebaseResult.Ok();
    }

    public async Task<FirebaseResult> DbGetAsync(string path)'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
