content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''        // Check for stale session from power outage'''

new = '''        // Check for updates in background (non-blocking)
        _ = Task.Run(async () =>
        {
            try
            {
                var version = GetVersion();
                await Services.AutoUpdateService.CheckAndUpdateAsync(version);
            }
            catch (Exception ex) { Log.Warning(ex, "[Update] Background update check failed"); }
        });

        // Check for stale session from power outage'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
