content = open(r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml', encoding='utf-8').read()
old = '                    <RadioButton x:Name="NavHelp" AutomationProperties.AutomationId="NavHelp" Tag="Help"'
new = '''                    <RadioButton x:Name="NavProfile" AutomationProperties.AutomationId="NavProfile" Tag="Profile"
                                 Style="{StaticResource SidebarNavButton}"
                                 Checked="NavButton_Checked" GroupName="Nav">
                        <StackPanel Orientation="Horizontal">
                            <TextBlock Text="&#xE77B;" FontFamily="Segoe MDL2 Assets"
                                       FontSize="16" VerticalAlignment="Center" Margin="0,0,10,0" />
                            <TextBlock Text="פרופיל" FontSize="15" VerticalAlignment="Center" />
                        </StackPanel>
                    </RadioButton>
                    <RadioButton x:Name="NavHelp" AutomationProperties.AutomationId="NavHelp" Tag="Help"'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
