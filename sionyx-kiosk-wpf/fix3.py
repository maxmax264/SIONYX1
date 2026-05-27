lines = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').readlines()
# מצא את ה-}} הכפול - שתי שורות עם רק } ברצף
for i in range(len(lines)-1):
    if lines[i].strip() == '}' and lines[i+1].strip() == '}' and i > 290:
        print(f'Found double }} at lines {i+1} and {i+2}')
        lines.pop(i+1)
        break
open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').writelines(lines)
print('OK')
