content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''    private SseListener? _remainingTimeListener;
    private SseListener? _idleRemainingTimeListener;
    private bool _isFirstRemainingTimeEvent = true;'''

new = '''    private SseListener? _remainingTimeListener;
    private SseListener? _idleRemainingTimeListener;
    private bool _isFirstRemainingTimeEvent = true;
    private bool _isIdleListener = false;'''

count = content.count(old)
print(f"Step 1: Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND - stop")
    exit()

old2 = '''        _idleRemainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("[SSE] Started idle remainingTime listener for user {UserId}", userId);'''

new2 = '''        _isIdleListener = true;
        _idleRemainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("[SSE] Started idle remainingTime listener for user {UserId}", userId);'''

count2 = content.count(old2)
print(f"Step 2: Found {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND - stop")
    exit()

old3 = '''        _isFirstRemainingTimeEvent = true;
        _remainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("[SSE] Started remainingTime listener for user {UserId}", _userId);'''

new3 = '''        _isFirstRemainingTimeEvent = true;
        _isIdleListener = false;
        _remainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("[SSE] Started remainingTime listener for user {UserId}", _userId);'''

count3 = content.count(old3)
print(f"Step 3: Found {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND - stop")
    exit()

old4 = '''        if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }'''

new4 = '''        if (_isFirstRemainingTimeEvent && !_isIdleListener) { _isFirstRemainingTimeEvent = false; return; }
        _isFirstRemainingTimeEvent = false;'''

count4 = content.count(old4)
print(f"Step 4: Found {count4} matches")
if count4 == 1:
    content = content.replace(old4, new4, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("Step 4: OK - file written")
else:
    print("Step 4: NOT FOUND - stop")
