content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', encoding='utf-8').read()

old = '            if (viewModel.CurrentUser?.IsAdmin == true)\n            {\n                _trayIcon = new SionyxKiosk.Services.TrayIconService();\n                _trayIcon.RestoreRequested += () => Dispatcher.Invoke(() => { WindowState = System.Windows.WindowState.Maximized; Topmost = true; Activate(); });\n                _trayIcon.OpenControlPanelRequested += () => Services.KioskPolicyService.RunWithControlPanel(() => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("control.exe") { UseShellExecute = true }));\n                _trayIcon.Show();\n            }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, '')
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('IsAdmin')
    print(repr(content[idx:idx+400]))
