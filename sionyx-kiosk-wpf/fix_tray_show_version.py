content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                            _trayIcon.Show();'
new = '                            _trayIcon.Show(GetVersion());'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
