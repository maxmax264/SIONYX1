content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old1 = '''    private bool _isFirstBudgetEvent = true;
'''
new1 = ''

count1 = content.count(old1)
print(f"Step 1 (field declaration): Found {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND - stop")
    exit()

old2 = '''        _isFirstBudgetEvent = true;
'''
new2 = ''

count2 = content.count(old2)
print(f"Step 2 (reset in Start): Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND - stop")
    exit()

old3 = '''            _isFirstBudgetEvent = false;
'''
new3 = ''

count3 = content.count(old3)
print(f"Step 3 (usage in handler): Found {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("Step 3: OK - file written")
else:
    print("Step 3: NOT FOUND - stop")
