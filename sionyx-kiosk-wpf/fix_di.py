content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = '                services.AddTransient<HelpPage>();'
new = '''                services.AddTransient<HelpPage>();
                services.AddTransient(sp => new ProfileViewModel(sp.GetRequiredService<AuthService>()));
                services.AddTransient(sp => new ProfilePage(sp.GetRequiredService<ProfileViewModel>()));'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
