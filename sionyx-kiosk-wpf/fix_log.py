f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = 'public double FormXPixels => FormX / 100.0 * System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth / 2;'
new = 'public double FormXPixels => FormX / 100.0 * System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth / 2;'

# הוסף לוג
old2 = 'partial void OnFormXChanged(double value) { OnPropertyChanged(nameof(FormXPixels)); OnPropertyChanged(nameof(FormMargin)); }'
new2 = 'partial void OnFormXChanged(double value) { Serilog.Log.Information("[Form] X={X} ScreenW={SW} FormW={FW} => Pixels={P}", FormX, System.Windows.SystemParameters.PrimaryScreenWidth, FormWidth, FormXPixels); OnPropertyChanged(nameof(FormXPixels)); OnPropertyChanged(nameof(FormMargin)); }'

count = c.count(old2)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old2, new2, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
