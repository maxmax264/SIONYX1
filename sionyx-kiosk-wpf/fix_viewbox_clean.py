f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''        <!-- Viewbox scales the auth card on screens smaller than 1000x700 -->
        <Viewbox HorizontalAlignment="Center" VerticalAlignment="Center"
                 Stretch="Uniform" StretchDirection="DownOnly"
                 MaxWidth="1000" MaxHeight="700" Margin="24">'''

new = '''        <!-- Viewbox scales the auth card on screens smaller than 1000x700 -->
        <Viewbox Stretch="Uniform" StretchDirection="DownOnly"
                 MaxHeight="700" Margin="24">
            <Viewbox.Style>
                <Style TargetType="Viewbox">
                    <Setter Property="HorizontalAlignment" Value="Center"/>
                    <Setter Property="VerticalAlignment" Value="Center"/>
                    <Setter Property="MaxWidth" Value="1000"/>
                    <Style.Triggers>
                        <DataTrigger Binding="{Binding CleanMode}" Value="True">
                            <Setter Property="HorizontalAlignment" Value="Left"/>
                            <Setter Property="VerticalAlignment" Value="Top"/>
                            <Setter Property="MaxWidth" Value="{Binding FormWidth}"/>
                            <Setter Property="Margin" Value="{Binding FormMargin}"/>
                        </DataTrigger>
                    </Style.Triggers>
                </Style>
            </Viewbox.Style>'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
