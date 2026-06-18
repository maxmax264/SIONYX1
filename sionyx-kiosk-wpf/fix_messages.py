content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

# תיקון 1: טאב מנהל — תגובת המשתמש צריכה להיות ימין
old = '''                                                <!-- תגובת המשתמש - ימין, סגול -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Margin="0,0,80,0">'''
new = '''                                                <!-- תגובת המשתמש - ימין, סגול -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Right"
                                                        Margin="80,0,0,0">'''
count = content.count(old)
print(f"Fix1: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print('Fix1: OK')
else:
    print('Fix1: NOT FOUND')

# תיקון 2: טאב פיקוח — הודעה מהפיקוח צריכה להיות שמאל
old2 = '''                                                <!-- הודעה מהפיקוח - שמאל, ירוק בהיר -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F0FDF4" Margin="80,0,0,0">'''
new2 = '''                                                <!-- הודעה מהפיקוח - שמאל, ירוק בהיר -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F0FDF4" Margin="0,0,80,0">'''
count2 = content.count(old2)
print(f"Fix2: Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print('Fix2: OK')
else:
    print('Fix2: NOT FOUND')

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
