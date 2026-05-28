content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

# 1. Log before budget check
old = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        if (budget >= cost)\n        {'
new = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        Logger.Debug("[PRINT] Budget check - need={Cost}, have={Budget}, doc={Doc}", cost, budget, docName);\n        if (budget >= cost)\n        {'
if old in content:
    content = content.replace(old, new, 1)
    print('Budget check log: OK')
else:
    print('Budget check log: NOT FOUND')

# 2. Log SPL retry result
old = '        Logger.Information("New print job detected: ID={JobId} on \'{Printer}\'", jobId, printer);'
new = '        Logger.Information("New print job detected: ID={JobId} on \'{Printer}\' - processing", jobId, printer);'
if old in content:
    content = content.replace(old, new, 1)
    print('Job detected log: OK')
else:
    print('Job detected log: NOT FOUND')

# 3. Log live printBalance update with more detail
old = '            Logger.Information("[PRINT] Live printBalance update: {Old} -> {New}", _cachedBudget, newBalance);'
new = '            Logger.Information("[PRINT] Live printBalance update from Firebase: {Old} -> {New} (delta={Delta})", _cachedBudget, newBalance, newBalance - (_cachedBudget ?? 0));'
if old in content:
    content = content.replace(old, new, 1)
    print('Live balance log: OK')
else:
    print('Live balance log: NOT FOUND')

# 4. Log InitializeKnownJobs result
old = '        Logger.Information("Found {Count} printer(s)", printers.Count);'
new = '        Logger.Information("[PRINT] Found {Count} printer(s) on startup", printers.Count);'
if old in content:
    content = content.replace(old, new, 1)
    print('Printers log: OK')
else:
    print('Printers log: NOT FOUND')

open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
