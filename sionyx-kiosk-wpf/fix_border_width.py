f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''<Border CornerRadius="20" ClipToBounds="True"
                Background="White">
            <Border.Style>
                <Style TargetType="Border">
                    <Setter Property="Width" Value="1000"/>
                    <Setter Property="Height" Value="700"/>
                    <Style.Triggers>
                        <DataTrigger Binding="{Binding CleanMode}" Value="True">
                            <Setter Property="Width" Value="500"/>
                            <Setter Property="Height" Value="700"/>
                        </DataTrigger>
                    </Style.Triggers>
                </Style>
            </Border.Style>'''

new = '''<Border CornerRadius="20" ClipToBounds="True"
                Background="White">
            <Border.Style>
                <Style TargetType="Border">
                    <Setter Property="Width" Value="1000"/>
                    <Setter Property="Height" Value="700"/>
                    <Style.Triggers>
                        <DataTrigger Binding="{Binding CleanMode}" Value="True">
                            <Setter Property="Width" Value="{Binding FormWidth}"/>
                            <Setter Property="Height" Value="700"/>
                        </DataTrigger>
                    </Style.Triggers>
                </Style>
            </Border.Style>'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
