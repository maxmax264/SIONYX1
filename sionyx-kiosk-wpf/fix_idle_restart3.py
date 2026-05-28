content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '_remainingTimeListener = null;\n\n        // Stop operating hours monitoring'
new = '_remainingTimeListener = null;\n        // Restart idle listener so dashboard updates show after session ends\n        _isFirstRemainingTimeEvent = true;\n        _idleRemainingTimeListener = Firebase.DbListen(\n            $"users/{_userId}/remainingTime",\n            OnRemainingTimeUpdated);\n\n        // Stop operating hours monitoring'

count = content.count(old)
print(f'Found {count} matches')
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
