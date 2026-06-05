path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'if (uid != null) { await Task.Delay(2000); _forceLogout.StartListening(uid); }',
    'if (uid != null) { await Task.Delay(4000); _forceLogout.StartListening(uid); }'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
