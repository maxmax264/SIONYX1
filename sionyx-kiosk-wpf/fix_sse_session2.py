content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '        OperatingHours.StartMonitoring();\n\n        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);'
new = '        OperatingHours.StartMonitoring();\n        // Listen for live remainingTime updates from Firebase\n        _isFirstRemainingTimeEvent = true;\n        _remainingTimeListener = Firebase.DbListen(\n            $"users/{_userId}/remainingTime",\n            OnRemainingTimeUpdated);\n        Logger.Information("[SSE] Started remainingTime listener for user {UserId}", _userId);\n\n        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
