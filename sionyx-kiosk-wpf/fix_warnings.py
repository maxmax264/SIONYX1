content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', encoding='utf-8').read()

old = '            string autoLoginUser = null;\n            foreach (var (username, cb) in checkBoxes)\n            {\n                if (cb.IsChecked == true) { autoLoginUser = username; break; }\n            }\n            SetAutoLogin(autoLoginUser);'

new = '            string? autoLoginUser = null;\n            foreach (var (username, cb) in checkBoxes)\n            {\n                if (cb.IsChecked == true) { autoLoginUser = username; break; }\n            }\n            SetAutoLogin(autoLoginUser ?? string.Empty);'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
