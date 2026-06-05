content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
content = content.replace(
    'if (!result.Success)\n            return Error(result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0");',
    'if (!result.IsSuccess)\n            return Error(result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0");'
)
open(r'.\src\SionyxKiosk\Services\AuthService.cs', 'w', encoding='utf-8').write(content)
print('OK')
