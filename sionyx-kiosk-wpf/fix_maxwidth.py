f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '                        <DataTrigger Binding="{Binding CleanMode}" Value="True">\n                            <Setter Property="HorizontalAlignment" Value="Left"/>\n                            <Setter Property="VerticalAlignment" Value="Top"/>\n                            <Setter Property="MaxWidth" Value="{Binding FormWidth}"/>\n                            <Setter Property="Margin" Value="{Binding FormMargin}"/>\n                        </DataTrigger>'
new = '                        <DataTrigger Binding="{Binding CleanMode}" Value="True">\n                            <Setter Property="HorizontalAlignment" Value="Left"/>\n                            <Setter Property="VerticalAlignment" Value="Top"/>\n                            <Setter Property="Margin" Value="{Binding FormMargin}"/>\n                        </DataTrigger>'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
    idx = c.find('DataTrigger Binding="{Binding CleanMode}"')
    print(repr(c[idx:idx+300]))
