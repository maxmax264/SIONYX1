content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

# הגדלת הודעת מנהל
old = '''                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F1F5F9" Margin="0,0,80,0">'''
new = '''                                                <Border CornerRadius="14" Padding="14,12"
                                                        MaxWidth="380" MinWidth="160" HorizontalAlignment="Left"
                                                        Background="#F1F5F9" Margin="0,0,80,0">'''
count = content.count(old)
print(f"Fix admin size: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix admin size: OK")
else:
    print("Fix admin size: NOT FOUND")

# הגדלת הודעת פיקוח
old2 = '''                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Margin="0,0,80,0"
                                                        FlowDirection="LeftToRight">'''
new2 = '''                                                <Border CornerRadius="14" Padding="14,12"
                                                        MaxWidth="380" MinWidth="160" HorizontalAlignment="Left"
                                                        Margin="0,0,80,0"
                                                        FlowDirection="LeftToRight">'''
count2 = content.count(old2)
print(f"Fix supervisor size: Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix supervisor size: OK")
else:
    print("Fix supervisor size: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
