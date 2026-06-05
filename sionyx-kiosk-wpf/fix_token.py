content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
old = '''    public async Task<ServiceResult> ChangePasswordAsync(string newPassword)
    {
        var result = await Firebase.ChangePasswordAsync(newPassword);
        if (!result.Success)
            return Error(result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0");
        return Success();
    }'''
new = '''    public async Task<ServiceResult> ChangePasswordAsync(string newPassword)
    {
        var result = await Firebase.ChangePasswordAsync(newPassword);
        if (!result.IsSuccess)
            return Error(result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0");
        // Save new token after password change
        if (!string.IsNullOrEmpty(Firebase.RefreshToken))
            _localDb.Set("refresh_token", Firebase.RefreshToken);
        return Success();
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND - trying alternative')
    # try with encoded hebrew
    idx = content.find('public async Task<ServiceResult> ChangePasswordAsync')
    print(repr(content[idx:idx+200]))
