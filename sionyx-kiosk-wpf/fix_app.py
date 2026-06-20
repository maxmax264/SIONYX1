content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = '''                            _trayIcon.ExitRequested += () =>
                            {
                                _trayIcon.Hide();
                                _trayIcon = null;
                                Shutdown();
                            };'''
new = '''                            _trayIcon.CheckUpdateRequested += () =>
                            {
                                _ = Task.Run(async () =>
                                {
                                    var version = GetVersion();
                                    var (hasUpdate, latestVersion, _) = await Services.AutoUpdateService.CheckForUpdateNowAsync(version);
                                    var msg = hasUpdate ? $"יש גרסה חדשה: {latestVersion}" : "מעודכן לגרסה האחרונה";
                                    Current.Dispatcher.Invoke(() => _trayIcon?.ShowBalloon("בדיקת עדכון", msg));
                                });
                            };
                            _trayIcon.ForceUpdateRequested += () =>
                            {
                                _ = Task.Run(async () =>
                                {
                                    var version = GetVersion();
                                    await Services.AutoUpdateService.ForceUpdateNowAsync(version, status =>
                                    {
                                        Current.Dispatcher.Invoke(() =>
                                        {
                                            _trayIcon?.SetUpdateStatus(status);
                                            _trayIcon?.ShowBalloon("עדכון SIONYX", status);
                                        });
                                    });
                                });
                            };
                            _trayIcon.ExitRequested += () =>
                            {
                                _trayIcon.Hide();
                                _trayIcon = null;
                                Shutdown();
                            };'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
