content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                _trayIcon.Hide();\n                                _trayIcon = null;\n                                var authWindow = new AuthWindow();\n                                MainWindow = authWindow;\n                                authWindow.Show();\n                            };'
new = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                _trayIcon.Hide();\n                                _trayIcon = null;\n                                var authVm = _host!.Services.GetRequiredService<ViewModels.AuthViewModel>();\n                                var authWindow = new AuthWindow(authVm);\n                                MainWindow = authWindow;\n                                authWindow.Show();\n                            };'
assert content.count(old) == 1, "not found"
content = content.replace(old, new)
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
