content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='cp1255').read()

old = 'OpenControlPanelRequested += () =>\n                            {\n                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo\n                                {\n                                    FileName = "control.exe",\n                                    UseShellExecute = true\n                                });\n                            };'
new = 'OpenControlPanelRequested += () =>\n                            {\n                                Services.KioskPolicyService.RunWithControlPanel(() =>\n                                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo\n                                    {\n                                        FileName = "control.exe",\n                                        UseShellExecute = true\n                                    }));\n                            };'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='cp1255').write(content)
    print('OK')
else:
    idx = content.find('OpenControlPanel')
    print(repr(content[idx:idx+400]))
