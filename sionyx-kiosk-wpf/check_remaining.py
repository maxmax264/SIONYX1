path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
raw = open(path, 'rb').read()
# חפש את דפוס ה-bytes המקולקל
import re
broken = re.findall(b'\xd7\xb3[\xe2\xc2][\x80\xa2\x9d\x9c\xa2]\xd7', raw)
print(f"Remaining broken sequences: {len(broken)}")
