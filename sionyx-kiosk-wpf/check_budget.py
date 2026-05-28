content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

# Find all occurrences of GetUserBudgetAsync with context
import re
for m in re.finditer(r'.{0,30}GetUserBudgetAsync\(forceRefresh: true\).{0,60}', content):
    print(repr(m.group()))
    print('---')
