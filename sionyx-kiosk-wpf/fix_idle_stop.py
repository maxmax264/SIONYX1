content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''        // Listen for live remainingTime updates from Firebase
        _isFirstRemainingTimeEvent = true;
        _remainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);'''
new = '''        // Stop idle listener and start session listener
        _idleRemainingTimeListener?.Stop();
        _idleRemainingTimeListener = null;
        _isFirstRemainingTimeEvent = true;
        _remainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - session start fixed')
else:
    print('NOT FOUND')
