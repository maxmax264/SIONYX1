path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs'
content = open(path, 'rb').read().decode('utf-8')

old = """                            _trayIcon.OpenControlPanelRequested += () =>
                            {
                                Services.KioskPolicyService.RunWithControlPanel(() =>
                                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                                    {
                                        FileName = "control.exe",
                                        UseShellExecute = true
                                    }));
                            };"""

new = """                            _trayIcon.OpenControlPanelRequested += async () =>
                            {
                                await Services.KioskPolicyService.RunWithControlPanelAsync(() =>
                                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                                    {
                                        FileName = "control.exe",
                                        UseShellExecute = true
                                    }));
                            };"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(path, 'wb').write(content.encode('utf-8'))
    print("OK")
else:
    print("Not found")
