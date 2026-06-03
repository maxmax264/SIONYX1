f = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8')
c = f.read()
f.close()
import re
for m in re.finditer(r'ShowAuthWindow|Logout|logout|SignOut|signout', c):
    print(f'Line context: {c[m.start()-50:m.start()+100]}')
    print()
