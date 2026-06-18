# -*- coding: utf-8 -*-
with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8') as f:
    content = f.read()

print("Sample of broken text found:")
import re
broken = re.findall(r'[^\x00-\x7F"\'@${}()\[\]<>/\\.,;:\s\-_=+!?#%^&*|~`]{2,}', content)
seen = set()
for b in broken:
    if b not in seen:
        print(repr(b))
        seen.add(b)
