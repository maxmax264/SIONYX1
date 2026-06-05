path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'if (eventType != "put" || data == null) return;',
    'if (eventType != "put" || data == null) return;\n        if (_isPaused) return;'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
