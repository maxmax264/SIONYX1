content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''    /// <summary>Update userId for a new login session (singleton reuse).</summary>
    public void Reinitialize(string userId)
    {
        _userId = userId;
        Logger.Information("Session service re-initialized for user: {UserId}", userId);
    }'''
new = '''    /// <summary>Update userId for a new login session (singleton reuse).</summary>
    public void Reinitialize(string userId)
    {
        _userId = userId;
        Logger.Information("Session service re-initialized for user: {UserId}", userId);
        // Start idle listener so dashboard updates show immediately even without active session
        _idleRemainingTimeListener?.Stop();
        _isFirstRemainingTimeEvent = true;
        _idleRemainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("[SSE] Started idle remainingTime listener for user {UserId}", userId);
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - Reinitialize')
else:
    print('NOT FOUND - Reinitialize')
