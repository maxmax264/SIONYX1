content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\SessionCoordinator.cs', encoding='utf-8').read()
old = '''    private void OnSessionEnded(string reason)
    {
        _printMonitor.StopMonitoring();
        _idleTimeout.StopMonitoring();
        Application.Current?.Dispatcher.InvokeAsync(() =>
        {
            CloseFloatingTimerInternal();
            RestoreMainWindow?.Invoke();
        });
    }'''
new = '''    private void OnSessionEnded(string reason)
    {
        _printMonitor.StopMonitoring();
        _idleTimeout.StopMonitoring();
        Application.Current?.Dispatcher.InvokeAsync(() =>
        {
            CloseFloatingTimerInternal();
            RestoreMainWindow?.Invoke();
        });
        // Install pending update after session ends
        _ = Task.Run(async () => await AutoUpdateService.TryInstallPendingUpdateAsync());
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\SessionCoordinator.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
