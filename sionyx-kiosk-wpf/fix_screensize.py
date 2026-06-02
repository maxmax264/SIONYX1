f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old1 = 'public double FormXPixels => FormX / 100.0 * System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth / 2;'
new1 = 'public double FormXPixels => FormX / 100.0 * 1600 - FormWidth / 2;'

old2 = 'public double FormYPixels => FormY / 100.0 * System.Windows.SystemParameters.PrimaryScreenHeight - 350;'
new2 = 'public double FormYPixels => FormY / 100.0 * 900 - 350;'

count1 = c.count(old1)
count2 = c.count(old2)
print(f'X:{count1} Y:{count2}')
if count1 == 1 and count2 == 1:
    c = c.replace(old1, new1, 1)
    c = c.replace(old2, new2, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
