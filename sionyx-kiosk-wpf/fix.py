lines = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').readlines()

new_block = [
'        // Run Firebase fetch and process cleanup in parallel\n',
'        var now = DateTime.Now.ToString("o");\n',
'        var fetchTask = FetchAndValidateUserAsync(initialRemainingTime);\n',
'        var cleanupTask = Task.Run(() => _processCleanup.CleanupUserProcesses());\n',
'        await Task.WhenAll(fetchTask, cleanupTask);\n',
'        var userCheck = fetchTask.Result;\n',
'        if (!userCheck.Valid) return Error(userCheck.ErrorMessage!);\n',
'        initialRemainingTime = userCheck.RemainingTime;\n',
'\n',
'        // Fire-and-forget session active update - dont block startup\n',
'        _ = Firebase.DbUpdateAsync($"users/{_userId}", new\n',
'        {\n',
'            isSessionActive = true,\n',
'            sessionStartTime = now,\n',
'            updatedAt = now,\n',
'        });\n',
]

# שורות 105-131 (index 104-130)
lines[104:131] = new_block

open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').writelines(lines)
print('OK')
