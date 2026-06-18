content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

# תיקון מנהל — הגדרת Grid עם FlowDirection
old = '''                                            <Grid Margin="0,0,0,10">
                                                <!-- הודעה מהמנהל - שמאל, אפור -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F1F5F9" Margin="0,0,80,0">'''
new = '''                                            <Grid Margin="0,0,0,10" FlowDirection="LeftToRight">
                                                <!-- הודעה מהמנהל - שמאל, אפור -->
                                                <Border CornerRadius="14" Padding="12,10"
                                                        MaxWidth="280" HorizontalAlignment="Left"
                                                        Background="#F1F5F9" Margin="0,0,80,0">'''
count = content.count(old)
print(f"Fix1: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix1: OK")
else:
    print("Fix1: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
