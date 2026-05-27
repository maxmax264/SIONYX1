content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''        // Run Firebase fetch and process cleanup in parallel
        var now = DateTime.Now.ToString("o");
        var fetchTask = FetchAndValidateUserAsync(initialRemainingTime);
        var cleanupTask = Task.Run(() => _processCleanup.CleanupUserProcesses());
        await Task.WhenAll(fetchTask, cleanupTask);
        var userCheck = fetchTask.Result;'''

new = '''        // Fetch user data from Firebase (blocking — need the result)
        var now = DateTime.Now.ToString("o");
        var fetchTask = FetchAndValidateUserAsync(initialRemainingTime);
        // Process cleanup runs in background — no reason to block session start
        _ = Task.Run(() =>
        {
            try { _processCleanup.CleanupUserProcesses(); }
            catch (Exception ex) { Logger.Warning(ex, "Process cleanup failed (non-fatal)"); }
        });
        var userCheck = await fetchTask;'''

open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content.replace(old, new))
print('OK' if old in content else 'NOT FOUND')
