content = open(r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', encoding='utf-8').read()
old = '                "Help" => _services.GetService(typeof(HelpPage)),'
new = '''                "Profile" => _services.GetService(typeof(ProfilePage)),
                "Help" => _services.GetService(typeof(HelpPage)),'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
