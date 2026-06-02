f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
lines = c.split('\n')
for i in range(60, 105):
    print(f'{i+1}: {lines[i]}')
