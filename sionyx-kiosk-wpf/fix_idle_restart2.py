content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '        _remainingTimeListener?.Stop();\r\n        _remainingTimeListener = null;\r\n        // Stop operating hours monitoring'
new = '        _remainingTimeListener?.Stop();\r\n        _remainingTimeListener = null;\r\n        // Restart idle listener so dashboard updates show after session ends\r\n        _isFirstRemainingTimeEvent = true;\r\n        _idleRemainingTimeListener = Firebase.DbListen(\r\n            \$\"users/{_userId}/remainingTime\",\r\n            OnRemainingTimeUpdated);\r\n        // Stop operating hours monitoring'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    old2 = old.replace('\r\n', '\n')
    count2 = content.count(old2)
    print(f"With LF only: {count2} matches")
    if count2 == 1:
        new2 = new.replace('\r\n', '\n')
        content = content.replace(old2, new2, 1)
        open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
        print('OK with LF')
    else:
        print('NOT FOUND')
