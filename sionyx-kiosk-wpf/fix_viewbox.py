f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '<Viewbox HorizontalAlignment="Center" VerticalAlignment="Center"\n                 Stretch="Uniform" StretchDirection="DownOnly"\n                 MaxWidth="1000" MaxHeight="700" Margin="24">'

new = '<Viewbox Stretch="Uniform" StretchDirection="DownOnly"\n                 MaxWidth="1000" MaxHeight="700" Margin="24">\n            <Viewbox.Style>\n                <Style TargetType="Viewbox">\n                    <Setter Property="HorizontalAlignment" Value="Center"/>\n                    <Setter Property="VerticalAlignment" Value="Center"/>\n                    <Style.Triggers>\n                        <DataTrigger Binding="{Binding CleanMode}" Value="True">\n                            <Setter Property="HorizontalAlignment" Value="Left"/>\n                            <Setter Property="VerticalAlignment" Value="Top"/>\n                            <Setter Property="Margin" Value="{Binding FormMargin}"/>\n                        </DataTrigger>\n                    </Style.Triggers>\n                </Style>\n            </Viewbox.Style>'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
