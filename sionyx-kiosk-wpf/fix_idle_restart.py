content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''        _remainingTimeListener?.Stop();
        _remainingTimeListener = null;
        // Stop operating hours monitoring'''
new = '''        _remainingTimeListener?.Stop();
        _remainingTimeListener = null;
        // Restart idle listener so dashboard updates show after session ends
        _isFirstRemainingTimeEvent = true;
        _idleRemainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        // Stop operating hours monitoring'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - idle listener restarted after session end')
else:
    print('NOT FOUND')
