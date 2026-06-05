path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'await _firebase.DbDeleteAsync($"organizations/sionov/users/{userId}/forceLogout");',
    'await _firebase.DbDeleteAsync($"users/{userId}/forceLogout");'
)
content = content.replace(
    'var path = $"organizations/sionov/users/{userId}/forceLogout";',
    'var path = $"users/{userId}/forceLogout";'
)
content = content.replace(
    '_ = _firebase.DbDeleteAsync($"organizations/sionov/users/{_userId}/forceLogout");',
    '_ = _firebase.DbDeleteAsync($"users/{_userId}/forceLogout");'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
