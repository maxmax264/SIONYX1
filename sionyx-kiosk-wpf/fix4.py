content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                            if (MainWindow is Views.Windows.MainWindow mainWin)\n                                mainWin.AllowClose();\n                            else if (MainWindow is AuthWindow aw)\n                                aw.AllowClose();'
new = '                            if (MainWindow is Views.Windows.MainWindow mainWin)\n                            { mainWin.AllowClose(); mainWin.Close(); }\n                            else if (MainWindow is AuthWindow aw)\n                            { aw.AllowClose(); aw.Close(); }'
assert content.count(old) == 1, "not found"
content = content.replace(old, new)
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
