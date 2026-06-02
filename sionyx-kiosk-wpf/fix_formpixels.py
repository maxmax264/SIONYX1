f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = '[ObservableProperty] private double _formX = 50;\n    [ObservableProperty] private double _formY = 50;\n    [ObservableProperty] private double _formWidth = 340;'
new = '[ObservableProperty] private double _formX = 50;\n    [ObservableProperty] private double _formY = 50;\n    [ObservableProperty] private double _formWidth = 340;\n    public double FormXPixels => FormX / 100.0 * 1000;\n    public double FormYPixels => FormY / 100.0 * 700;'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
