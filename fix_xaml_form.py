content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '                <StackPanel x:Name="LoginPanel" Canvas.Left="500" Canvas.Top="0"\n                            Width="500" Height="700" Opacity="1"'
new = '                <StackPanel x:Name="LoginPanel" Canvas.Left="{Binding FormX}" Canvas.Top="{Binding FormY}"\n                            Width="{Binding FormWidth}" Height="700" Opacity="1"'

count = content.count(old)
print(f"LF: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    old2 = '                <StackPanel x:Name="LoginPanel" Canvas.Left="500" Canvas.Top="0"\r\n                            Width="500" Height="700" Opacity="1"'
    new2 = '                <StackPanel x:Name="LoginPanel" Canvas.Left="{Binding FormX}" Canvas.Top="{Binding FormY}"\r\n                            Width="{Binding FormWidth}" Height="700" Opacity="1"'
    count2 = content.count(old2)
    print(f"CRLF: {count2}")
    if count2 == 1:
        content = content.replace(old2, new2, 1)
        open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
        print('OK')
    else:
        print('NOT FOUND')
