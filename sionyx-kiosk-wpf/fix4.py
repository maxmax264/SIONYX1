content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()

old = '''                                            <Grid Margin="0,0,0,10">
                                                <!-- הודעה מהפיקוח - שמאל, ירוק בהיר -->'''
new = '''                                            <Grid Margin="0,0,0,10" FlowDirection="LeftToRight">
                                                <!-- הודעה מהפיקוח - שמאל, ירוק בהיר -->'''
count = content.count(old)
print(f"Fix supervisor: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Fix supervisor: OK")
else:
    print("Fix supervisor: NOT FOUND")

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
print('Done')
