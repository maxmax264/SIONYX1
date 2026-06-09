content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

# 1. Fix RestoreRequested - just show auth window instead of restart
old = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                var exe = System.Diagnostics.Process.GetCurrentProcess().MainModule!.FileName;\n                                System.Diagnostics.Process.Start(exe);\n                                System.Threading.Thread.Sleep(1500);\n                                _trayIcon?.Hide();\n                                _trayIcon = null;\n                                Shutdown();\n                            };'
new = '                            _trayIcon.RestoreRequested += () =>\n                            {\n                                _trayIcon?.Hide();\n                                _trayIcon = null;\n                                ShowAuthWindow();\n                            };'
assert content.count(old) == 1, "restore not found"
content = content.replace(old, new)

# 2. Fix OpenControlPanel - open Windows control panel
old = '                            _trayIcon.OpenControlPanelRequested += () =>\n                            {\n                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo\n                                {\n                                    FileName = "https://pc-sion.web.app",\n                                    UseShellExecute = true\n                                });\n                            };'
new = '                            _trayIcon.OpenControlPanelRequested += () =>\n                            {\n                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo\n                                {\n                                    FileName = "control.exe",\n                                    UseShellExecute = true\n                                });\n                            };\n                            _trayIcon.OpenDashboardRequested += () =>\n                            {\n                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo\n                                {\n                                    FileName = "https://pc-sion.web.app",\n                                    UseShellExecute = true\n                                });\n                            };'
assert content.count(old) == 1, "control panel not found"
content = content.replace(old, new)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
