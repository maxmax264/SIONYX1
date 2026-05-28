content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

# 1. Add fields
old = '    private const int BudgetCacheTtlSec = 30;'
new = '    private const int BudgetCacheTtlSec = 30;\n    private SseListener? _budgetListener;\n    private bool _isFirstBudgetEvent = true;'
if old not in content:
    print('FIELD NOT FOUND'); exit()
content = content.replace(old, new, 1)

# 2. Start listener in StartMonitoringAsync
old = '        Logger.Information("Print monitor started");\n    }'
new = '        _isFirstBudgetEvent = true;\n        _budgetListener = Firebase.DbListen(\n            $"users/{_userId}/printBalance",\n            OnPrintBalanceUpdated);\n        Logger.Information("Print monitor started");\n    }'
if old not in content:
    print('START NOT FOUND'); exit()
content = content.replace(old, new, 1)

# 3. Stop listener in StopMonitoring
old = '        Logger.Information("Stopping print monitor");\n        _isMonitoring = false;\n        _stopRequested = true;'
new = '        Logger.Information("Stopping print monitor");\n        _isMonitoring = false;\n        _stopRequested = true;\n        _budgetListener?.Stop();\n        _budgetListener = null;'
if old not in content:
    print('STOP NOT FOUND'); exit()
content = content.replace(old, new, 1)

# 4. Add handler before BUDGET section
old = '    // ==================== BUDGET ===================='
new = '''    private void OnPrintBalanceUpdated(string eventType, JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        try
        {
            if (_isFirstBudgetEvent) { _isFirstBudgetEvent = false; return; }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            double newBalance;
            if (data.Value.ValueKind == JsonValueKind.Number)
            {
                if (!data.Value.TryGetDouble(out newBalance)) return;
            }
            else if (data.Value.ValueKind == JsonValueKind.Object &&
                     data.Value.TryGetProperty("printBalance", out var pb))
            {
                if (!pb.TryGetDouble(out newBalance)) return;
            }
            else return;
            if (_cachedBudget.HasValue && Math.Abs(_cachedBudget.Value - newBalance) < 0.001) return;
            Logger.Information("[PRINT] Live printBalance update: {Old} -> {New}", _cachedBudget, newBalance);
            _cachedBudget = newBalance;
            _budgetCacheTime = DateTime.UtcNow;
            DispatchEvent(() => BudgetUpdated?.Invoke(newBalance));
        }
        catch (Exception ex) { Logger.Error(ex, "OnPrintBalanceUpdated error"); }
    }
    // ==================== BUDGET ===================='''
if '    // ==================== BUDGET ====================' not in content:
    print('BUDGET SECTION NOT FOUND'); exit()
content = content.replace('    // ==================== BUDGET ====================', new, 1)

open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
print('OK')
