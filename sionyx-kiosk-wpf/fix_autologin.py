content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''        // Check for stale session from power outage
        if (Services.SessionStateService.HasActiveSession())
        {
            Log.Warning("[Session] Stale session detected on startup - running cleanup");
            try
            {
                var browserCleanup = new Services.BrowserCleanupService();
                browserCleanup.CleanupWithBrowserClose();
                browserCleanup.CleanupDownloads();
            }
            catch (Exception ex) { Log.Error(ex, "[Session] Startup cleanup failed"); }
            Services.SessionStateService.ClearSession();
        }'''

new = '''        // Check for stale session from power outage
        if (Services.SessionStateService.HasActiveSession())
        {
            Log.Warning("[Session] Stale session detected on startup - running cleanup");
            try
            {
                var browserCleanup = new Services.BrowserCleanupService();
                browserCleanup.CleanupWithBrowserClose();
                browserCleanup.CleanupDownloads();
            }
            catch (Exception ex) { Log.Error(ex, "[Session] Startup cleanup failed"); }
            // Clear stored tokens so previous client cannot auto-login
            try
            {
                var localDb = _host!.Services.GetRequiredService<Infrastructure.LocalDatabase>();
                localDb.Delete("refresh_token");
                localDb.Delete("user_id");
                Log.Information("[Session] Cleared stored tokens after stale session cleanup");
            }
            catch (Exception ex) { Log.Warning(ex, "[Session] Could not clear tokens"); }
            Services.SessionStateService.ClearSession();
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
