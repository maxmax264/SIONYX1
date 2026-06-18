path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# תיקון Title ו-TextBlock הראשי
replacements = [
    ('Title="\u05d2\u05e3\u05e2\u05e7\u05d7\u05d5\u05e7\u05d8"', 'Title="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea"'),
]

# נחפש את הטקסט המקולקל בפועל
import re
broken = re.findall(r'[\u05f3\u05f4\xd7\xb3\xb4\xb9\xb7\xb6\xb8\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb5\xba\xbb\xbc\xbd\xbe\xbf]+', content)
print("Sample broken sequences found:")
for b in set(broken[:10]):
    print(repr(b))

# החלפה ישירה של הכותרות המקולקלות
old1 = content[content.find("Title="):content.find("Title=")+50]
print(f"\nTitle line: {repr(old1)}")
