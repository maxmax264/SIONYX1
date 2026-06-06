content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
old = '''    private void ShowMainWindow()
    {
        Log.Debug("Creating MainWindow from DI");
        var mainWindow = _host!.Services.GetRequiredService<MainWindow>();
        var mainVm = (MainViewModel)mainWindow.DataContext;

        mainVm.LogoutRequested += OnLogoutRequested;'''
new = '''    private void ShowMainWindow()
    {
        Log.Debug("Creating MainWindow from DI");

        // Reinitialize HomeViewModel with the current (fresh) user
        var auth = _host!.Services.GetRequiredService<AuthService>();
        var homeVm = _host!.Services.GetRequiredService<HomeViewModel>();
        if (auth.CurrentUser != null)
            homeVm.Reinitialize(auth.CurrentUser);

        var mainWindow = _host!.Services.GetRequiredService<MainWindow>();
        var mainVm = (MainViewModel)mainWindow.DataContext;

        mainVm.LogoutRequested += OnLogoutRequested;'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
