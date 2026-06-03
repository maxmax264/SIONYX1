f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
idx = c.find('ReloadBackgroundAsync')
print(c[idx:idx+400])
print('---')
# מצא את כל הקריאות ל-LoadBackgroundAsync
import re
for m in re.finditer(r'LoadBackgroundAsync|ReloadBackgroundAsync', c):
    print(f'offset {m.start()}: {c[m.start()-50:m.start()+60]}')
    print()
