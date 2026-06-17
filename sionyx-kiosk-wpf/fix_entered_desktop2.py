content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = 'IsActive = true;\n        _warned5Min = false;\n        _warned1Min = false;\n\n        // Start timers'

new = 'IsActive = true;\n        _warned5Min = false;\n        _warned1Min = false;\n\n        // Mark that user entered desktop in Registry\n        SessionStateService.SetEnteredDesktop(true);\n\n        // Start timers'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
