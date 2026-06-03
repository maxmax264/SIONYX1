f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
old = 'public double FormYPixels => Math.Max(0, FormY / 100.0 * (System.Windows.SystemParameters.PrimaryScreenHeight - 500));'
new = 'public double FormYPixels => Math.Max(0, FormY / 100.0 * (System.Windows.SystemParameters.PrimaryScreenHeight - 700));'
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
