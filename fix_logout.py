content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = '''    private void OnLogoutRequested()
    {
        _ = Current.Dispatcher.InvokeAsync(async () =>
        {
            try
            {
                await StopSystemServicesAsync();

                _host!.Services.GetRequiredService<PrintHistoryService>().Clear();

                var auth = _host!.Services.GetRequiredService<AuthService>();
                await auth.LogoutAsync();

                if (MainWindow is Views.Windows.MainWindow mw)
                {
                    mw.AllowClose();
                    mw.Close();
                }
                ShowAuthWindow();
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Error during logout");
            }
        });
    }'''
new = '''    private void OnLogoutRequested()
    {
        _ = Current.Dispatcher.InvokeAsync(async () =>
        {
            try
            {
                await StopSystemServicesAsync();

                _host!.Services.GetRequiredService<PrintHistoryService>().Clear();

                var auth = _host!.Services.GetRequiredService<AuthService>();
                await auth.LogoutAsync();

                // Clean browser data so next user sees no trace of previous user
                await Task.Run(() =>
                {
                    try
                    {
                        _host!.Services.GetRequiredService<BrowserCleanupService>().CleanupWithBrowserClose();
                    }
                    catch (Exception ex)
                    {
                        Log.Error(ex, "Browser cleanup failed during logout (non-fatal)");
                    }
                });

                if (MainWindow is Views.Windows.MainWindow mw)
                {
                    mw.AllowClose();
                    mw.Close();
                }
                ShowAuthWindow();
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Error during logout");
            }
        });
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
