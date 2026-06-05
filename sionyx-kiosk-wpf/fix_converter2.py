content = open(r'.\src\SionyxKiosk\Views\Pages\ProfilePage.xaml', encoding='utf-8').read()
content = content.replace('IsEnabled="{Binding IsBusy, Converter={StaticResource InverseBool}}"', '')
open(r'.\src\SionyxKiosk\Views\Pages\ProfilePage.xaml', 'w', encoding='utf-8').write(content)
print('OK')
