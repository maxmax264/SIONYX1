content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''        IsActive = true;
        _warned5Min = false;
        _warned1Min = false;
        // Start timers'''

new = '''        IsActive = true;
        _warned5Min = false;
        _warned1Min = false;
        // Mark that user entered desktop in Registry
        SessionStateService.SetEnteredDesktop(true);
        // Start timers'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
