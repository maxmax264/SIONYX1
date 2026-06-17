import re, sys

path = r'.\src\SionyxKiosk\App.xaml.cs'
content = open(path, encoding='utf-8').read()

old = r'        _host = Host.CreateDefaultBuilder()'
new = r'        _host = Host.CreateDefaultBuilder()' + '\n' + r'            .UseContentRoot(AppContext.BaseDirectory)'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
