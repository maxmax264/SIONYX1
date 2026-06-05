path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'private bool _isPaused;',
    'private volatile bool _isPaused;'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
