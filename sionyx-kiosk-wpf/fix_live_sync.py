content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

# 1. Add SSE listener field after _warned1Min
old = '''    private bool _warned1Min;'''
new = '''    private bool _warned1Min;
    // Live sync from Firebase
    private SseListener? _remainingTimeListener;
    private bool _isFirstRemainingTimeEvent = true;'''
content = content.replace(old, new, 1)

# 2. Start SSE listener at end of StartSessionAsync
old = '''        OperatingHours.StartMonitoring();
        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);
        SessionStarted?.Invoke();
        return Success(new { SessionId });'''
new = '''        OperatingHours.StartMonitoring();
        _isFirstRemainingTimeEvent = true;
        _remainingTimeListener = Firebase.DbListen(
            $"users/{_userId}/remainingTime",
            OnRemainingTimeUpdated);
        Logger.Information("Session started (remaining: {Time}s)", initialRemainingTime);
        SessionStarted?.Invoke();
        return Success(new { SessionId });'''
content = content.replace(old, new, 1)

# 3. Stop SSE listener in EndSessionAsync
old = '''        _countdownTimer.Stop();
        _syncTimer.Stop();'''
new = '''        _countdownTimer.Stop();
        _syncTimer.Stop();
        _remainingTimeListener?.Stop();
        _remainingTimeListener = null;'''
content = content.replace(old, new, 1)

# 4. Add handler method before UserValidationResult
old = '''    private record UserValidationResult(bool Valid, int RemainingTime, string? ErrorMessage);'''
new = '''    private void OnRemainingTimeUpdated(string eventType, System.Text.JsonElement? data)
    {
        if (eventType != "put" || data == null) return;
        try
        {
            if (_isFirstRemainingTimeEvent) { _isFirstRemainingTimeEvent = false; return; }
            if (data.Value.ValueKind == JsonValueKind.Null) return;
            if (!data.Value.TryGetInt32(out var newTime)) return;
            if (newTime == RemainingTime) return;
            Logger.Information("[SESSION] Live remainingTime update: {Old}s -> {New}s", RemainingTime, newTime);
            _initialRemainingTime = newTime;
            StartTime = DateTime.UtcNow;
            TimeUsed = 0;
            RemainingTime = newTime;
            TimeUpdated?.Invoke(RemainingTime);
        }
        catch (Exception ex) { Logger.Error(ex, "OnRemainingTimeUpdated error"); }
    }
    private record UserValidationResult(bool Valid, int RemainingTime, string? ErrorMessage);'''
content = content.replace(old, new, 1)

if '_remainingTimeListener' in content and 'OnRemainingTimeUpdated' in content:
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
