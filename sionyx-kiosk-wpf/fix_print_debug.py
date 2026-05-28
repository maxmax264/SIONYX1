content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '    private void OnPrintBalanceUpdated(string eventType, JsonElement? data)\n    {\n        if (eventType != "put" || data == null) return;\n        try\n        {\n            if (_isFirstBudgetEvent) { _isFirstBudgetEvent = false; return; }'
new = '    private void OnPrintBalanceUpdated(string eventType, JsonElement? data)\n    {\n        Logger.Debug("[PRINT-SSE] Raw event: type={Type} data={Data}", eventType, data?.ToString() ?? "null");\n        if (eventType != "put" || data == null) return;\n        try\n        {\n            if (_isFirstBudgetEvent) { _isFirstBudgetEvent = false; return; }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
