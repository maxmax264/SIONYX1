content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\r\n        if (budget >= cost)\r\n        {'
new = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\r\n        Logger.Debug("[PRINT] Budget check - need={Cost}x, have={Budget}x, doc={Doc}", cost, budget, docName);\r\n        if (budget >= cost)\r\n        {'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
elif count > 1:
    print('Multiple - need more context')
else:
    print('Still not found')
