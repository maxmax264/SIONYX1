f = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
lines = f.readlines()
f.close()
for i, line in enumerate(lines[275:310], start=276):
    print(f'{i}: {line}', end='')
