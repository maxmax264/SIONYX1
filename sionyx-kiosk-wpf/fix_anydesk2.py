content = open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', encoding='utf-8').read()

old = '    private readonly HashSet<int> _recentlyBlocked = new();'
new = '    private readonly HashSet<int> _recentlyBlocked = new();\n    private readonly HashSet<int> _permanentlyFailed = new();'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - field added')
else:
    print('NOT FOUND')
