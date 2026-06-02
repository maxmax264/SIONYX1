content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '    [ObservableProperty] private bool _cleanMode = false;'
new = '''    [ObservableProperty] private bool _cleanMode = false;
    [ObservableProperty] private double _formX = 500;
    [ObservableProperty] private double _formY = 0;
    [ObservableProperty] private double _formWidth = 500;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
