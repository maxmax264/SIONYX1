content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
old = '''    public async Task<ServiceResult> ChangePasswordAsync(string newPassword)
    {
        var result = await Firebase.ChangePasswordAsync(newPassword);
        if (!result.IsSuccess)
            return Error(result.Error ?? "שגיאה בשינוי הסיסמה");
        if (!string.IsNullOrEmpty(Firebase.RefreshToken))
            _localDb.Set("refresh_token", Firebase.RefreshToken);
        return Success();
    }'''
new = '''    public async Task<ServiceResult> ChangePasswordAsync(string newPassword)
    {
        var result = await Firebase.ChangePasswordAsync(newPassword);
        if (!result.IsSuccess)
            return Error(result.Error ?? "שגיאה בשינוי הסיסמה");
        if (!string.IsNullOrEmpty(Firebase.RefreshToken))
            _localDb.Set("refresh_token", Firebase.RefreshToken);
        // Re-save userId so auto-login still works
        if (!string.IsNullOrEmpty(Firebase.UserId))
            _localDb.Set("user_id", Firebase.UserId);
        return Success();
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('ChangePasswordAsync')
    print(repr(content[idx:idx+300]))
