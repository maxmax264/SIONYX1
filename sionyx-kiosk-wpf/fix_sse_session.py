content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '        OperatingHours.StartMonitoring();\n        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);'
new = '        OperatingHours.StartMonitoring();\n        // Listen for live remainingTime updates from Firebase (e.g. admin adds time)\n        _isFirstRemainingTimeEvent = true;\n        _remainingTimeListener = Firebase.DbListen(\n            $"users/{_userId}/remainingTime",\n            OnRemainingTimeUpdated);\n        Logger.Information("[SSE] Started remainingTime listener for user {UserId}", _userId);\n        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    # try with \r\n
    old2 = old.replace('\n', '\r\n')
    count2 = content.count(old2)
    print(f"With CRLF: {count2} matches")
    if count2 == 1:
        new2 = new.replace('\n', '\r\n')
        content = content.replace(old2, new2, 1)
        open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
        print('OK with CRLF')
