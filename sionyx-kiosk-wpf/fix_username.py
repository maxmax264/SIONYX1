path = r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs'
c = open(path, encoding='utf-8').read()
c = c.replace('_user.Username', '_user.FullName')
open(path, 'w', encoding='utf-8').write(c)
print('OK')
