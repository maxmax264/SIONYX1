f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = 'public double FormXPixels => FormX / 100.0 * 1000;\n    public double FormYPixels => FormY / 100.0 * 700;'
new = 'public double FormXPixels => FormX / 100.0 * 1000;\n    public double FormYPixels => FormY / 100.0 * 700;\n    partial void OnFormXChanged(double value) => OnPropertyChanged(nameof(FormXPixels));\n    partial void OnFormYChanged(double value) => OnPropertyChanged(nameof(FormYPixels));'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
