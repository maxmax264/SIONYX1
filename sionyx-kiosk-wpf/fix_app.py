content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

# 1. Add _trayIcon field
old = '    private SystemServicesManager? _systemServices;\n    private SessionCoordinator? _sessionCoordinator;'
new = '    private SystemServicesManager? _systemServices;\n    private SessionCoordinator? _sessionCoordinator;\n    private TrayIconService? _trayIcon;'
assert content.count(old) == 1, "field not found"
content = content.replace(old, new)

# 2. Replace Shutdown() block with tray show
old = '''                if (password == expectedPassword)
                {
                    Log.Information("Admin exit: correct password, shutting down");
                    _ = Task.Run(async () =>
                    {
                        await StopSystemServicesAsync();
                        _host!.Services.GetRequiredService<PrintHistoryService>().Clear();
                        await auth.LogoutAsync();
                        Current.Dispatcher.Invoke(() =>
                        {
                            if (MainWindow is Views.Windows.MainWindow mainWin)
                                mainWin.AllowClose();
                            else if (MainWindow is AuthWindow aw)
                                aw.AllowClose();
                            Shutdown();
                        });
                    });
                }'''
new = '''                if (password == expectedPassword)
                {
                    Log.Information("Admin exit: correct password, showing tray");
                    _ = Task.Run(async () =>
                    {
                        await StopSystemServicesAsync();
                        _host!.Services.GetRequiredService<PrintHistoryService>().Clear();
                        await auth.LogoutAsync();
                        Current.Dispatcher.Invoke(() =>
                        {
                            if (MainWindow is Views.Windows.MainWindow mainWin)
                                mainWin.AllowClose();
                            else if (MainWindow is AuthWindow aw)
                                aw.AllowClose();
                            _trayIcon = new TrayIconService();
                            _trayIcon.RestoreRequested += () =>
                            {
                                _trayIcon.Hide();
                                _trayIcon = null;
                                var authWindow = new AuthWindow();
                                MainWindow = authWindow;
                                authWindow.Show();
                            };
                            _trayIcon.OpenControlPanelRequested += () =>
                            {
                                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                                {
                                    FileName = "https://pc-sion.web.app",
                                    UseShellExecute = true
                                });
                            };
                            _trayIcon.ExitRequested += () =>
                            {
                                _trayIcon.Hide();
                                _trayIcon = null;
                                Shutdown();
                            };
                            _trayIcon.Show();
                        });
                    });
                }'''
assert content.count(old) == 1, "shutdown block not found"
content = content.replace(old, new)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
