content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '                <Border x:Name="BrandOverlay" Canvas.Left="-3" Canvas.Top="-3"'
new = '                <Border x:Name="BrandOverlay" Canvas.Left="-3" Canvas.Top="-3"\n                        Visibility="{Binding CleanMode, Converter={StaticResource InverseBoolToVis}}"'

if old in content:
    content = content.replace(old, new, 1)
    print("LF: OK")
else:
    old2 = old.replace('\n', '\r\n')
    new2 = new.replace('\n', '\r\n')
    if old2 in content:
        content = content.replace(old2, new2, 1)
        print("CRLF: OK")
    else:
        print("NOT FOUND")

open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
