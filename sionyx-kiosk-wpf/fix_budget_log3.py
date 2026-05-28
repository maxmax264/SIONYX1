content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = 'private async Task HandlePausedJobAsync(string printerName, int jobId, string docName, int billablePages, double cost)\r\n    {\r\n        var budget = await GetUserBudgetAsync(forceRefresh: true);\r\n        if (budget >= cost)'
new = 'private async Task HandlePausedJobAsync(string printerName, int jobId, string docName, int billablePages, double cost)\r\n    {\r\n        var budget = await GetUserBudgetAsync(forceRefresh: true);\r\n        Logger.Debug("[PRINT] Budget check - need={Cost}x, have={Budget}x, doc={Doc}", cost, budget, docName);\r\n        if (budget >= cost)'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    # Try without \r
    old2 = old.replace('\r\n', '\n')
    count2 = content.count(old2)
    print(f"Without CR: {count2} matches")
