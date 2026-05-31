xaml = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8').read()

old = '        <ScrollViewer Grid.Row="4" VerticalScrollBarVisibility="Auto" Padding="0">'
new = '        <ScrollViewer Grid.Row="4" VerticalScrollBarVisibility="Auto" Padding="0" Visibility="{Binding IsPurchasesTabVisible, Converter={StaticResource BoolToVis}}">'

count = xaml.count(old)
print(f"Found: {count}")
if count == 1:
    xaml = xaml.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(xaml)
    print("OK")
else:
    print("NOT FOUND")
