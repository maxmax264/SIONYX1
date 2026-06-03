f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
import re
for m in re.finditer(r'Phone|Password|Reset|Clear', c):
    print(c[m.start()-20:m.start()+80])
    print()
