f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
old = 'public double FormXPixels => Math.Max(0, (1.0 - FormX / 100.0) * (System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth));'
new = 'public double FormXPixels => Math.Max(0, (FormX / 100.0) * (System.Windows.SystemParameters.PrimaryScreenWidth - FormWidth));'
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
