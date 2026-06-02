f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
old = '<Border CornerRadius="20" Background="White" ClipToBounds="True"\n                Width="1000" Height="700"\n                Visibility="{Binding CleanMode, Converter={StaticResource InverseBoolToVis}}">'
new = '<Border CornerRadius="20" ClipToBounds="True"\n                Width="1000" Height="700">\n            <Border.Style>\n                <Style TargetType="Border">\n                    <Setter Property="Background" Value="White"/>\n                    <Style.Triggers>\n                        <DataTrigger Binding="{Binding CleanMode}" Value="True">\n                            <Setter Property="Background" Value="Transparent"/>\n                        </DataTrigger>\n                    </Style.Triggers>\n                </Style>\n            </Border.Style>'
count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
