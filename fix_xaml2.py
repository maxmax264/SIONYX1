content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()

old = '''                            <TextBlock Text="ברוכים הבאים" Style="{StaticResource TextH1}" Margin="0,0,0,6" />
                            <TextBlock Text="התחבר לחשבון שלך"
                                       Style="{StaticResource TextSubtitle}" Margin="0,0,0,36" />'''

new = '''                            <TextBlock Text="{Binding WelcomeText}" Style="{StaticResource TextH1}" Margin="0,0,0,6" />
                            <TextBlock Text="{Binding WelcomeSubtext}"
                                       Style="{StaticResource TextSubtitle}" Margin="0,0,0,36" />'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
