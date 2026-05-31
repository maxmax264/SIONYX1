content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''private async Task FinalSyncAsync(string reason)
    {
        Logger.Information("[SYNC] Final sync - reason={Reason}, remainingTime={Time}s, timeUsed={Used}s", reason, RemainingTime, TimeUsed);
        await Firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object?>
        {
            ["remainingTime"] = Math.Max(0, RemainingTime),
            ["isSessionActive"] = false,
            ["sessionStartTime"] = null,
            ["updatedAt"] = DateTime.Now.ToString("o"),
        });
    }'''

new = '''private async Task FinalSyncAsync(string reason)
    {
        Logger.Information("[SYNC] Final sync - reason={Reason}, remainingTime={Time}s, timeUsed={Used}s", reason, RemainingTime, TimeUsed);
        await Firebase.DbUpdateAsync($"users/{_userId}", new Dictionary<string, object?>
        {
            ["remainingTime"] = Math.Max(0, RemainingTime),
            ["isSessionActive"] = false,
            ["sessionStartTime"] = null,
            ["updatedAt"] = DateTime.Now.ToString("o"),
        });

        // Save session log
        try
        {
            var logKey = $"{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
            var orgId = Firebase.OrgId;
            await Firebase.DbUpdateAsync($"organizations/{orgId}/sessionLogs/{_userId}/{logKey}", new Dictionary<string, object?>
            {
                ["userId"] = _userId,
                ["startTime"] = StartTime?.ToString("o"),
                ["endTime"] = DateTime.Now.ToString("o"),
                ["usedSeconds"] = TimeUsed,
                ["remainingSeconds"] = Math.Max(0, RemainingTime),
                ["reason"] = reason,
                ["computerId"] = DeviceInfo.GetDeviceId(),
                ["computerName"] = RegistryConfig.ReadValue("ComputerName") ?? DeviceInfo.GetComputerName(),
            });
            Logger.Information("[LOG] Session log saved for user {UserId}", _userId);
        }
        catch (Exception ex)
        {
            Logger.Warning(ex, "[LOG] Failed to save session log (non-fatal)");
        }
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
