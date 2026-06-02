f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '        <Viewbox Stretch="Uniform" StretchDirection="DownOnly"\n                 MaxHeight="700" Margin="24">'
new = '        <Viewbox Stretch="Uniform" StretchDirection="DownOnly"\n                 MaxHeight="700" Margin="24"\n                 HorizontalAlignment="Center" VerticalAlignment="Center">'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND - trying raw')
    idx = c.find('<Viewbox Stretch="Uniform"')
    print(repr(c[idx:idx+100]))
