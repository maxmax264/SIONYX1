content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
old = '    /// <summary>Update current user\'s data in Firebase.</summary>'
new = '''    /// <summary>Change current user password in Firebase Auth.</summary>
    public async Task<ServiceResult> ChangePasswordAsync(string newPassword)
    {
        var result = await Firebase.ChangePasswordAsync(newPassword);
        if (!result.Success)
            return Error(result.Error ?? "שגיאה בשינוי הסיסמה");
        return Success();
    }
    /// <summary>Update current user\'s data in Firebase.</summary>'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
