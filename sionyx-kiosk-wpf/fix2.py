content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

# תיקון מנהל — תגובת המשתמש: FlowDirection + ימין אמיתי
old = '                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Right"\n                                                        Margin="80,0,0,0">'
new = '                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Right"\n                                                        FlowDirection="LeftToRight"\n                                                        Margin="80,0,0,0">'
count = content.count(old)
print(f"Fix1: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix1: OK")
else:
    print("Fix1: NOT FOUND")

# תיקון פיקוח — תגובת המשתמש: FlowDirection + ימין אמיתי
old2 = '                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Right"\n                                                        Margin="0,0,80,0">'
new2 = '                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Right"\n                                                        FlowDirection="LeftToRight"\n                                                        Margin="0,0,80,0">'
count2 = content.count(old2)
print(f"Fix2: Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix2: OK")
else:
    print("Fix2: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
