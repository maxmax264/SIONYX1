xaml = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8').read()

old1 = 'Visibility="{Binding IsSessionsTabVisible, FallbackValue=Collapsed}"'
new1 = 'Visibility="{Binding IsSessionsTabVisible, Converter={StaticResource BoolToVis}}"'

old2 = 'Visibility="{Binding IsPrintsTabVisible, FallbackValue=Collapsed}"'
new2 = 'Visibility="{Binding IsPrintsTabVisible, Converter={StaticResource BoolToVis}}"'

c1 = xaml.count(old1)
c2 = xaml.count(old2)
print(f"Sessions: {c1}, Prints: {c2}")

if c1 == 1:
    xaml = xaml.replace(old1, new1, 1)
    print("Sessions OK")
if c2 == 1:
    xaml = xaml.replace(old2, new2, 1)
    print("Prints OK")

open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(xaml)
