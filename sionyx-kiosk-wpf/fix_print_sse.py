content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '''            if (_isFirstBudgetEvent) { _isFirstBudgetEvent = false; return; }'''
new = '''            _isFirstBudgetEvent = false;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK - file written")
else:
    print("NOT FOUND - stop")
