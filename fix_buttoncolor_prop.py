f = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
old = '[ObservableProperty] private string _overlayColor1 = "#6366F1";'
new = '[ObservableProperty] private string _overlayColor1 = "#6366F1";\n    [ObservableProperty] private string _buttonColor = "";'
count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
