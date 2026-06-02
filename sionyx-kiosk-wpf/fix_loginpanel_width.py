f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = 'x:Name="LoginPanel" Canvas.Top="0"\n                            Width="500" Height="700" Opacity="1"'
new = 'x:Name="LoginPanel" Canvas.Top="0"\n                            Height="700" Opacity="1"'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
