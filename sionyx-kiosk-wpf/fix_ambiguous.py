import re
path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml.cs'
content = open(path, encoding='utf-8').read()
if 'using System.Windows.Input;' not in content:
    content = 'using System.Windows.Input;\n' + content
content = content.replace('KeyEventArgs', 'System.Windows.Input.KeyEventArgs')
open(path, 'w', encoding='utf-8').write(content)
print('AuthWindow OK')

path2 = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs'
content2 = open(path2, encoding='utf-8').read()
content2 = content2.replace('KeyEventArgs', 'System.Windows.Input.KeyEventArgs')
open(path2, 'w', encoding='utf-8').write(content2)
print('MainWindow OK')
