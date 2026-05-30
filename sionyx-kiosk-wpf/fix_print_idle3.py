content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '''    public void StopMonitoring()
    {
        if (!_isMonitoring) return;

        Logger.Information("Stopping print monitor");
        _isMonitoring = false;
        _stopRequested = true;
        _budgetListener?.Stop();
        _budgetListener = null;

        _notificationThread?.Join(TimeSpan.FromSeconds(3));
        _notificationThread = null;'''

new = '''    public void StopMonitoring()
    {
        if (!_isMonitoring) return;

        Logger.Information("Stopping print monitor");
        _isMonitoring = false;
        _stopRequested = true;
        _budgetListener?.Stop();
        _budgetListener = null;

        _notificationThread?.Join(TimeSpan.FromSeconds(3));
        _notificationThread = null;

        // Restart idle listener so dashboard updates show after session ends
        if (!string.IsNullOrEmpty(_userId))
        {
            _idleBudgetListener?.Stop();
            _idleBudgetListener = Firebase.DbListen(
                $"users/{_userId}/printBalance",
                OnPrintBalanceUpdated);
            Logger.Information("[SSE] Restarted idle printBalance listener for user {UserId}", _userId);
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK - file written")
else:
    print("NOT FOUND - stop")
