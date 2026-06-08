content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = "        authVm.ResetForm();\n        authVm.LoginSucceeded -= OnLoginSucceeded;"
new = "        authVm.ResetForm();\n        _ = authVm.ReloadBackgroundAsync();\n        authVm.LoginSucceeded -= OnLoginSucceeded;"
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
