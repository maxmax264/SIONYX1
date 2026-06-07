content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''        authVm.LoginSucceeded += OnLoginSucceeded;
        authVm.RegistrationSucceeded += OnLoginSucceeded;'''

new = '''        authVm.LoginSucceeded -= OnLoginSucceeded;
        authVm.RegistrationSucceeded -= OnLoginSucceeded;
        authVm.LoginSucceeded += OnLoginSucceeded;
        authVm.RegistrationSucceeded += OnLoginSucceeded;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
