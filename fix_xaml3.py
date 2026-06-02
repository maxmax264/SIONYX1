content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '''                            <Button AutomationProperties.AutomationId="SwitchToRegisterLink" Content="אין לך חשבון? הירשם"
                                    Style="{StaticResource BtnGhost}" Margin="0,12,0,0"
                                    Click="ToggleToRegister_Click" />'''

new = '''                            <Button AutomationProperties.AutomationId="SwitchToRegisterLink" Content="אין לך חשבון? הירשם"
                                    Style="{StaticResource BtnGhost}" Margin="0,12,0,0"
                                    Click="ToggleToRegister_Click"
                                    Visibility="{Binding ShowRegister, Converter={StaticResource BoolToVis}}" />'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
