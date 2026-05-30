content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '''    public void Reinitialize(string userId)
    {
        StopMonitoring();
        _userId = userId;
        _cachedBudget = null;
        _budgetCacheTime = null;
    }'''

new = '''    private SseListener? _idleBudgetListener;

    public void Reinitialize(string userId)
    {
        StopMonitoring();
        _userId = userId;
        _cachedBudget = null;
        _budgetCacheTime = null;
        // Start idle listener so dashboard updates show immediately even without active session
        _idleBudgetListener?.Stop();
        _idleBudgetListener = Firebase.DbListen(
            $"users/{_userId}/printBalance",
            OnPrintBalanceUpdated);
        Logger.Information("[SSE] Started idle printBalance listener for user {UserId}", userId);
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK - file written")
else:
    print("NOT FOUND - stop")
