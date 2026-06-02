import re
with open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8') as f:
    content = f.read()

old = '<StackPanel x:Name="LoginPanel" Canvas.Left="{Binding FormX}" Canvas.Top="{Binding FormY}"\n                            Width="{Binding FormWidth}" Height="700" Opacity="1"'
new = '<StackPanel x:Name="LoginPanel" Canvas.Left="500" Canvas.Top="0"\n                            Width="500" Height="700" Opacity="1"'

if old in content:
    content = content.replace(old, new)
    print("LF: OK")
else:
    old = old.replace('\n', '\r\n')
    new = new.replace('\n', '\r\n')
    if old in content:
        content = content.replace(old, new)
        print("CRLF: OK")
    else:
        print("NOT FOUND")
        exit()

with open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8') as f:
    f.write(content)
