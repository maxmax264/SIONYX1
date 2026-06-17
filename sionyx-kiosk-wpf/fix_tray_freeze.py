content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

# 1. הוסף משתנה _frozenSession
old1 = '    private SystemServicesManager? _systemServices;\n    private SessionCoordinator? _sessionCoordinator;\n    private TrayIconService? _trayIcon;'
new1 = '    private SystemServicesManager? _systemServices;\n    private SessionCoordinator? _sessionCoordinator;\n    private TrayIconService? _trayIcon;\n    private bool _hasFrozenSession = false; // true when admin exits while client is logged in'

count1 = content.count(old1)
print(f"Fix 1: {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Fix 1 OK")
else:
    print("Fix 1 NOT FOUND")

# 2. שנה RestoreRequested להחזיר ללקוח אם יש הקפאה
old2 = '''_trayIcon.RestoreRequested += () =>
                            {
                                _trayIcon?.Hide();
                                _trayIcon = null;
                                ShowAuthWindow();
                            };'''
new2 = '''_trayIcon.RestoreRequested += () =>
                            {
                                _trayIcon?.Hide();
                                _trayIcon = null;
                                if (_hasFrozenSession)
                                {
                                    _hasFrozenSession = false;
                                    // Restore to existing client session
                                    Current.Dispatcher.Invoke(() =>
                                    {
                                        var mainWindow = _host?.Services.GetService<Views.Windows.MainWindow>();
                                        if (mainWindow != null)
                                        {
                                            mainWindow.WindowState = System.Windows.WindowState.Maximized;
                                            mainWindow.Topmost = true;
                                            mainWindow.Show();
                                            mainWindow.Activate();
                                            MainWindow = mainWindow;
                                            _systemServices?.StartGlobalHotkey();
                                        }
                                    });
                                }
                                else
                                {
                                    ShowAuthWindow();
                                }
                            };'''

count2 = content.count(old2)
print(f"Fix 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix 2 OK")
else:
    print("Fix 2 NOT FOUND")

# 3. סמן _hasFrozenSession=true כשיש לקוח מחובר ומנהל יוצא
old3 = '''            if (dialog.ShowDialog() == true)
            {
                var password = dialog.EnteredPassword;'''
new3 = '''            if (dialog.ShowDialog() == true)
            {
                var password = dialog.EnteredPassword;'''

# בדוק אם MainWindow הוא MainWindow (לקוח מחובר) לפני שמגדיר _hasFrozenSession
old4 = '''                    _ = Task.Run(async () =>
                    {
                        await StopSystemServicesAsync();
                        _host!.Services.GetRequiredService<PrintHistoryService>().Clear();
                        await auth.LogoutAsync();
                        Current.Dispatcher.Invoke(() =>
                        {
                            if (MainWindow is Views.Windows.MainWindow mainWin)
                            { mainWin.AllowClose(); mainWin.Close(); }
                            else if (MainWindow is AuthWindow aw)
                            { aw.AllowClose(); aw.Close(); }
                            _trayIcon = new TrayIconService();'''
new4 = '''                    _ = Task.Run(async () =>
                    {
                        // Check if a client session is active before stopping services
                        var auth2 = _host?.Services.GetService<AuthService>();
                        bool clientWasActive = auth2?.CurrentUser != null;
                        await StopSystemServicesAsync();
                        _host!.Services.GetRequiredService<PrintHistoryService>().Clear();
                        await auth.LogoutAsync();
                        Current.Dispatcher.Invoke(() =>
                        {
                            _hasFrozenSession = clientWasActive;
                            if (MainWindow is Views.Windows.MainWindow mainWin && !clientWasActive)
                            { mainWin.AllowClose(); mainWin.Close(); }
                            else if (MainWindow is AuthWindow aw)
                            { aw.AllowClose(); aw.Close(); }
                            _trayIcon = new TrayIconService();'''

count4 = content.count(old4)
print(f"Fix 4: {count4} matches")
if count4 == 1:
    content = content.replace(old4, new4, 1)
    print("Fix 4 OK")
else:
    print("Fix 4 NOT FOUND")

open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print("DONE")
