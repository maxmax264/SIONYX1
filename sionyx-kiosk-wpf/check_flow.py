f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '                    <Setter Property="HorizontalAlignment" Value="Center"/>'
new = '                    <Setter Property="HorizontalAlignment" Value="Center" />'

# בדוק את ה-FlowDirection על ה-Viewbox
idx = c.find('Viewbox')
print(c[idx:idx+500])
