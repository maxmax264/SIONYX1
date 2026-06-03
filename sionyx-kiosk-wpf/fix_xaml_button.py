f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '                                Background="{Binding DataContext.OverlayGradient, RelativeSource={RelativeSource AncestorType=Window}}"'
new = '                                Background="{Binding DataContext.ButtonGradient, RelativeSource={RelativeSource AncestorType=Window}}"'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
