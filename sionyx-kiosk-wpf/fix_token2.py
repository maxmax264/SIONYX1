content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
old = '        return Success();\n    }\n    /// <summary>Update'
new = '        if (!string.IsNullOrEmpty(Firebase.RefreshToken))\n            _localDb.Set("refresh_token", Firebase.RefreshToken);\n        return Success();\n    }\n    /// <summary>Update'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
