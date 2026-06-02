f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '<Setter Property="Canvas.Left" Value="{Binding FormX}"/>\n                                    <Setter Property="Canvas.Top" Value="{Binding FormY}"/>'
new = '<Setter Property="Canvas.Left" Value="{Binding FormXPixels}"/>\n                                    <Setter Property="Canvas.Top" Value="{Binding FormYPixels}"/>'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
