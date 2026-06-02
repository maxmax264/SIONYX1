f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

# החזר את Canvas.Left="500" ל-LoginPanel
old = '<StackPanel x:Name="LoginPanel" Canvas.Top="0"'
new = '<StackPanel x:Name="LoginPanel" Canvas.Left="500" Canvas.Top="0"'
count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
