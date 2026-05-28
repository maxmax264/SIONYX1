content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '        var budget = await GetUserBudgetAsync(forceRefresh: true);\n        if (budget >= cost)\n        {'
count = content.count(old)
print(f"Exact matches: {count}")

import re
for m in re.finditer(r'var budget = await GetUserBudgetAsync\(forceRefresh: true\);\n.{0,80}', content):
    print(repr(m.group()))
    print('---')
