xaml = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8').read()

# Fix purchases ScrollViewer to Row 4
old = '        <ScrollViewer Grid.Row="3" VerticalScrollBarVisibility="Auto" Padding="0">'
new = '        <!-- Tab buttons -->\n        <StackPanel Grid.Row="3" Orientation="Horizontal" Margin="0,0,0,8">\n            <RadioButton Content="\u05e8\u05db\u05d9\u05e9\u05d5\u05ea" IsChecked="{Binding IsPurchasesTab, Mode=TwoWay}" GroupName="HistoryTabs" Margin="0,0,8,0"/>\n            <RadioButton Content="\u05e9\u05d9\u05de\u05d5\u05e9" IsChecked="{Binding IsSessionsTab, Mode=TwoWay}" GroupName="HistoryTabs" Margin="0,0,8,0"/>\n            <RadioButton Content="\u05d4\u05d3\u05e4\u05e1\u05d5\u05ea" IsChecked="{Binding IsPrintsTab, Mode=TwoWay}" GroupName="HistoryTabs"/>\n        </StackPanel>\n        <ScrollViewer Grid.Row="4" VerticalScrollBarVisibility="Auto" Padding="0">'

count = xaml.count(old)
print(f"Found: {count}")
if count == 1:
    xaml = xaml.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(xaml)
    print("OK")
else:
    print("NOT FOUND")
