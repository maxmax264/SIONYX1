content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

# 1. Add SSE listener field after _budgetCacheTime
old = '''    private const int BudgetCacheTtlSec = 30;'''
new = '''    private const int BudgetCacheTtlSec = 30;
    // Live budget sync from Firebase
    private SseListener? _budgetListener;
    private bool _isFirstBudgetEvent = true;'''
content = content.replace(old, new, 1)

# 2. Start SSE listener in StartMonitoringAsync
old = '''        Logger.Information("Print monitor started");
    }'''
new = '''        // Listen for live printBalance updates from Firebase (e.g. admin tops up)
        _isFirstBudgetEvent = true;
        _budgetListener = Firebase.DbListen(
            $"users/{_userId}/printBalance",
            OnPrintBalanceUpdated);
        Logger.Information("Print monitor started");
    }'''
content = content.replace(old, new, 1)

# 3. Stop SSE listener in StopMonitoring
old = '''        Logger.Information("Stopping print monitor");
        _isMonitoring = false;
        _stopRequested = true;'''
new = '''        Logger.Information("Stopping print monitor");
        _isMonitoring = false;
        _stopRequested = true;
        _budgetListener?.Stop();
        _budgetListener = null;'''
content = content.replace(old, new, 1)

# 4. Add handler method before BUDGET section
old = '''    // ==================== BUDGET ===================='''
new = '''    private void OnPrintBalanceUpdated(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        try
        {
            if (_isFirstBudgetEvent) { _isFirstBudgetEvent = false; return; }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            if (!data.Value.TryGetDouble(out var newBalance)) return;
            if (_cachedBudget.HasValue && Math.Abs(_cachedBudget.Value - newBalance) < 0.001) return;
            Logger.Information("[PRINT] Live printBalance update from Firebase: {Old} -> {New}",
                _cachedBudget, newBalance);
            _cachedBudget = newBalance;
            _budgetCacheTime = DateTime.UtcNow;
            DispatchEvent(() => BudgetUpdated?.Invoke(newBalance));
        }
        catch (Exception ex) { Logger.Error(ex, "OnPrintBalanceUpdated error"); }
    }
    // ==================== BUDGET ===================='''
content = content.replace(old, new, 1)

if '_budgetListener' in content and 'OnPrintBalanceUpdated' in content:
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
