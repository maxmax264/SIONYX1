f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''x:Name="LoginPanel" Canvas.Top="0"
                            Width="500" Height="700" Opacity="1"
                            FlowDirection="RightToLeft">
                    <StackPanel.Style>
                        <Style TargetType="StackPanel">
                            <Setter Property="Canvas.Left" Value="500"/>
                            <Style.Triggers>
                                <DataTrigger Binding="{Binding CleanMode}" Value="True">
                                    <Setter Property="Canvas.Left" Value="0"/>
                                </DataTrigger>
                            </Style.Triggers>
                        </Style>
                    </StackPanel.Style>'''

new = '''x:Name="LoginPanel" Canvas.Top="0"
                            Width="500" Height="700" Opacity="1"
                            FlowDirection="RightToLeft">
                    <StackPanel.Style>
                        <Style TargetType="StackPanel">
                            <Setter Property="Canvas.Left" Value="500"/>
                            <Setter Property="Width" Value="500"/>
                            <Style.Triggers>
                                <DataTrigger Binding="{Binding CleanMode}" Value="True">
                                    <Setter Property="Canvas.Left" Value="0"/>
                                    <Setter Property="Width" Value="{Binding FormWidth}"/>
                                </DataTrigger>
                            </Style.Triggers>
                        </Style>
                    </StackPanel.Style>'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
