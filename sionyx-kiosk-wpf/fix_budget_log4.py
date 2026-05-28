content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = 'private async Task HandlePausedJobAsync(string printerName, int jobId, string docName, int billablePages, double cost)\n    {\n        var budget = await GetUserBudgetAsync(forceRefresh: true);\n\n        if (budget >= cost)'
new = 'private async Task HandlePausedJobAsync(string printerName, int jobId, string docName, int billablePages, double cost)\n    {\n        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        Logger.Debug("[PRINT] Budget check - need={Cost}x, have={Budget}x, doc={Doc}", cost, budget, docName);\n\n        if (budget >= cost)'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
