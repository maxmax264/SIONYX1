content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', encoding='utf-8').read()

old = '_trayIcon.OpenControlPanelRequested += () => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("control.exe") { UseShellExecute = true });'
new = '_trayIcon.OpenControlPanelRequested += () => Services.KioskPolicyService.RunWithControlPanel(() => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("control.exe") { UseShellExecute = true }));'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('OpenControlPanel')
    print(repr(content[idx:idx+200]))
