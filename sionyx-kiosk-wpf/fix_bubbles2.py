import re

path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# הודעות נכנסות (מהמנהל) - Left -> Right
old2 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                                        Background="#F1F5F9" Margin="0,0,80,0"'
new2 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                                        Background="#F1F5F9" Margin="80,0,0,0"'

# הודעות יוצאות (אתה) - Right -> Left  
old3 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                                        Margin="80,0,0,0"'
new3 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                                        Margin="0,0,80,0"'

print(f"Incoming: {content.count(old2)}")
print(f"Outgoing: {content.count(old3)}")

if content.count(old2) >= 1 and content.count(old3) >= 1:
    content = content.replace(old2, new2)
    content = content.replace(old3, new3)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND - checking line endings")
    print(repr(content[content.find('HorizontalAlignment="Left"')-10:content.find('HorizontalAlignment="Left"')+80]))
