content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', encoding='utf-8').read()

old = '        btnSave.Click += (s, e) =>\n        {\n            foreach (var (username, cb) in checkBoxes)\n            {\n                SetStartupForUser(username, cb.IsChecked == true);\n            }\n            MessageBox.Show("\u05d4\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea \u05e0\u05e9\u05de\u05e8\u05d5!", "\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea", MessageBoxButton.OK, MessageBoxImage.Information);\n            Close();\n        };'

new = '        btnSave.Click += (s, e) =>\n        {\n            // Find the single enabled user for auto-login\n            string autoLoginUser = null;\n            foreach (var (username, cb) in checkBoxes)\n            {\n                if (cb.IsChecked == true) { autoLoginUser = username; break; }\n            }\n            SetAutoLogin(autoLoginUser);\n            MessageBox.Show("\u05d4\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea \u05e0\u05e9\u05de\u05e8\u05d5!", "\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea", MessageBoxButton.OK, MessageBoxImage.Information);\n            Close();\n        };'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Dialogs\StartupSettingsDialog.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('btnSave.Click')
    print(repr(content[idx:idx+300]))
