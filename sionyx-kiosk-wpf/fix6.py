content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                                var version = Infrastructure.AppVersion.Get();'
new = '                                var version = GetVersion();'
assert content.count(old) == 1, "not found"
content = content.replace(old, new)
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
