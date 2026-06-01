f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml.cs', encoding='utf-8')
c = f.read()
f.close()

old = '        Loaded += (_, _) => LoginPhoneInput.Focus();'
new = '        Loaded += (_, _) => { LoginPhoneInput.Focus(); _ = viewModel.ReloadBackgroundAsync(); };'

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml.cs', 'w', encoding='utf-8').write(c)
print("OK")
