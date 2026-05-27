path = r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs'
c = open(path, encoding='utf-8').read()
old = 'using SionyxKiosk.Views.Pages;\nnamespace SionyxKiosk.Views.Windows;'
new = 'using SionyxKiosk.Views.Pages;\nusing Serilog;\nnamespace SionyxKiosk.Views.Windows;'
if old in c:
    open(path, 'w', encoding='utf-8').write(c.replace(old, new))
    print('OK')
else:
    print('NOT FOUND')
    print(repr(c[c.find('Views.Pages'):c.find('Views.Pages')+60]))
