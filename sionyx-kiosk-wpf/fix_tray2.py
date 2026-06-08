content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', encoding='utf-8').read()
old = "    private readonly MainViewModel _vm;\n    private readonly IServiceProvider _services;\n    private bool _initialized;\n    private bool _allowClose;\n    private Page? _currentPage;"
new = "    private readonly MainViewModel _vm;\n    private readonly IServiceProvider _services;\n    private bool _initialized;\n    private bool _allowClose;\n    private Page? _currentPage;\n    private SionyxKiosk.Services.TrayIconService? _trayIcon;"
count = content.count(old)
print(f"patch1: {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("patch1 OK")
else:
    print("patch1 NOT FOUND")
    exit(1)

old2 = "        Loaded += (_, _) =>\n        {\n            Dispatcher.InvokeAsync(() => NavigateToPage(\"Home\"), System.Windows.Threading.DispatcherPriority.Loaded);\n            UpdateAvatarInitials();\n        };"
new2 = "        Loaded += (_, _) =>\n        {\n            Dispatcher.InvokeAsync(() => NavigateToPage(\"Home\"), System.Windows.Threading.DispatcherPriority.Loaded);\n            UpdateAvatarInitials();\n            if (viewModel.CurrentUser?.IsAdmin == true)\n            {\n                _trayIcon = new SionyxKiosk.Services.TrayIconService();\n                _trayIcon.RestoreRequested += () => Dispatcher.Invoke(() => { WindowState = System.Windows.WindowState.Maximized; Topmost = true; Activate(); });\n                _trayIcon.OpenControlPanelRequested += () => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(\"control.exe\") { UseShellExecute = true });\n                _trayIcon.Show();\n            }\n        };"
count2 = content.count(old2)
print(f"patch2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("patch2 OK")
else:
    print("patch2 NOT FOUND")
    exit(1)

old3 = "        if (!_allowClose)\n        {\n            e.Cancel = true;\n            return;\n        }\n        base.OnClosing(e);"
new3 = "        _trayIcon?.Hide();\n        _trayIcon?.Dispose();\n        _trayIcon = null;\n        if (!_allowClose)\n        {\n            e.Cancel = true;\n            return;\n        }\n        base.OnClosing(e);"
count3 = content.count(old3)
print(f"patch3: {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("patch3 OK")
else:
    print("patch3 NOT FOUND")
    exit(1)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', 'w', encoding='utf-8').write(content)
print("DONE")
