path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
raw = open(path, 'rb').read()
import re

# מצא את כל האזורים המקולקלים עם הקונטקסט שלהם
for m in re.finditer(b'[^\n]{0,30}\xd7\xb3[\xe2\xc2].{1,20}\xd7[^\n]{0,30}', raw):
    print(repr(m.group()))
    print()
