content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                _trayIcon.Hide();\n                                _trayIcon = null;\n                                var exe = System.Diagnostics.Process.GetCurrentProcess().MainModule!.FileName;\n                                System.Diagnostics.Process.Start(exe);\n                                Shutdown();\n                            };'
new = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                var exe = System.Diagnostics.Process.GetCurrentProcess().MainModule!.FileName;\n                                System.Diagnostics.Process.Start(exe);\n                                System.Threading.Thread.Sleep(1500);\n                                _trayIcon?.Hide();\n                                _trayIcon = null;\n                                Shutdown();\n                            };'
assert content.count(old) == 1, "not found: " + str(content.count(old))
content = content.replace(old, new)
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
