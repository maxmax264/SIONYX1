content = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8').read()
old = '<Border CornerRadius="20" Background="White" ClipToBounds="True"\n                Width="1000" Height="700">'
new = '<Border CornerRadius="20" Background="White" ClipToBounds="True"\n                Width="1000" Height="700"\n                Visibility="{Binding CleanMode, Converter={StaticResource InverseBoolToVis}}">'
count = content.count(old)
print(f'Found {count} matches')
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
