content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

# 1. Add Debug log to SyncToFirebaseAsync - success case
old = '        if (result.Success)\n        {\n            if (_consecutiveSyncFailures > 0)\n            {\n                _consecutiveSyncFailures = 0;\n                IsOnline = true;\n                SyncRestored?.Invoke();\n            }\n        }'
new = '        if (result.Success)\n        {\n            Logger.Debug("[SYNC] Firebase sync OK - remainingTime={Time}s", RemainingTime);\n            if (_consecutiveSyncFailures > 0)\n            {\n                _consecutiveSyncFailures = 0;\n                IsOnline = true;\n                Logger.Information("[SYNC] Connection restored after {Count} failures", _consecutiveSyncFailures);\n                SyncRestored?.Invoke();\n            }\n        }'
if old in content:
    content = content.replace(old, new, 1)
    print('Sync success log: OK')
else:
    print('Sync success log: NOT FOUND')

# 2. Add Debug log to FinalSyncAsync
old = '    private async Task FinalSyncAsync(string reason)\n    {\n        await Firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object?>'
new = '    private async Task FinalSyncAsync(string reason)\n    {\n        Logger.Information("[SYNC] Final sync - reason={Reason}, remainingTime={Time}s, timeUsed={Used}s", reason, RemainingTime, TimeUsed);\n        await Firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object?>'
if old in content:
    content = content.replace(old, new, 1)
    print('Final sync log: OK')
else:
    print('Final sync log: NOT FOUND')

# 3. Add Debug log to SSE remainingTime handler
old = '            Logger.Information("[SESSION] Live remainingTime update: {Old}s -> {New}s", RemainingTime, newTime);'
new = '            Logger.Information("[SESSION] Live remainingTime update: {Old}s -> {New}s (delta={Delta}s)", RemainingTime, newTime, newTime - RemainingTime);'
if old in content:
    content = content.replace(old, new, 1)
    print('SSE time log: OK')
else:
    print('SSE time log: NOT FOUND')

open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
