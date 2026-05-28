content = open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', encoding='utf-8').read()

old = '                    if (_recentlyBlocked.Contains(pid)) continue;'
new = '                    if (_recentlyBlocked.Contains(pid)) continue;\n                    if (_permanentlyFailed.Contains(pid)) continue;'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - check added')
else:
    print('NOT FOUND')
