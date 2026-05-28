content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        if (budget >= cost)\n        {'
new = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        Logger.Debug("[PRINT] Budget check - need={Cost}x, have={Budget}x, doc={Doc}", cost, budget, docName);\n        if (budget >= cost)\n        {'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
elif count > 1:
    print('Multiple matches - need to be more specific')
else:
    # Try to find what's actually there
    idx = content.find('GetUserBudgetAsync(forceRefresh: true)')
    print(repr(content[idx-10:idx+80]))
