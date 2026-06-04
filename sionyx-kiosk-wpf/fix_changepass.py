content = open(r'.\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', encoding='utf-8').read()
old = '    public async Task<FirebaseResult> DbDeleteAsync(string path)'
new = '''    public async Task<FirebaseResult> ChangePasswordAsync(string newPassword)
    {
        var url = $"{_authUrl}:update?key={_apiKey}";
        var payload = new { idToken = _idToken, password = newPassword, returnSecureToken = true };
        try
        {
            var response = await PostJsonAsync(url, payload);
            StoreAuthData(response);
            Logger.Information("Password changed for user: {UserId}", _userId);
            return FirebaseResult.Ok(null);
        }
        catch (Exception ex)
        {
            var msg = ParseFirebaseError(ex);
            Logger.Error(ex, "Change password failed");
            return FirebaseResult.Fail(msg);
        }
    }
    public async Task<FirebaseResult> DbDeleteAsync(string path)'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
