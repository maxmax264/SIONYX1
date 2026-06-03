f = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8')
c = f.read()
f.close()

old = '        var authVm = _host!.Services.GetRequiredService<AuthViewModel>();\n        // AuthViewModel is Transient (new instance each time) so event subscriptions\n        // are fresh and don\'t leak.\n        authVm.LoginSucceeded += OnLoginSucceeded;'
new = '        var authVm = _host!.Services.GetRequiredService<AuthViewModel>();\n        authVm.ResetForm();\n        // AuthViewModel is Singleton - reset form on each show\n        authVm.LoginSucceeded += OnLoginSucceeded;'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
