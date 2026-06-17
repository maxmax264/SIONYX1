content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

# 1. בעלייה — בדיקת session פתוח אחרי כיבוי
old1 = '        ShowAuthWindow();\n    }\n    // ================================================================\n    // Window Lifecycle'
new1 = '''        // Check for stale session from power outage
        if (Services.SessionStateService.HasActiveSession())
        {
            Log.Warning("[Session] Stale session detected on startup — running cleanup");
            try
            {
                var browserCleanup = new Services.BrowserCleanupService();
                browserCleanup.CleanupWithBrowserClose();
                browserCleanup.CleanupDownloads();
            }
            catch (Exception ex) { Log.Error(ex, "[Session] Startup cleanup failed"); }
            Services.SessionStateService.ClearSession();
        }

        ShowAuthWindow();
    }
    // ================================================================
    // Window Lifecycle'''

count1 = content.count(old1)
print(f"Fix 1 (startup check): {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Fix 1 OK")
else:
    print("Fix 1 NOT FOUND")

# 2. כשלקוח מתחיל שימוש — SetSessionActive
old2 = '''    private void StartSystemServices()
    {
        try
        {
            var auth = _host!.Services.GetRequiredService<AuthService>();
            var userId = auth.CurrentUser?.Uid ?? "";
            if (string.IsNullOrEmpty(userId))
            {
                Log.Warning("StartSystemServices called without a logged-in user");
                return;
            }

            var session = _host.Services.GetRequiredService<SessionService>();
            session.Reinitialize(userId);

            _sessionCoordinator!.Subscribe();
            _systemServices!.Start(userId, _isKiosk);'''

new2 = '''    private void StartSystemServices()
    {
        try
        {
            var auth = _host!.Services.GetRequiredService<AuthService>();
            var userId = auth.CurrentUser?.Uid ?? "";
            if (string.IsNullOrEmpty(userId))
            {
                Log.Warning("StartSystemServices called without a logged-in user");
                return;
            }

            // Mark session as active in Registry (survives power outage)
            Services.SessionStateService.SetSessionActive(userId);

            var session = _host.Services.GetRequiredService<SessionService>();
            session.Reinitialize(userId);

            _sessionCoordinator!.Subscribe();
            _systemServices!.Start(userId, _isKiosk);'''

count2 = content.count(old2)
print(f"Fix 2 (SetSessionActive): {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Fix 2 OK")
else:
    print("Fix 2 NOT FOUND")

# 3. כשלקוח יוצא — ClearSession
old3 = '''                var browserCleanup = _host!.Services.GetRequiredService<BrowserCleanupService>();
                        browserCleanup.CleanupWithBrowserClose();
                        browserCleanup.CleanupDownloads();'''

new3 = '''                var browserCleanup = _host!.Services.GetRequiredService<BrowserCleanupService>();
                        browserCleanup.CleanupWithBrowserClose();
                        browserCleanup.CleanupDownloads();
                        Services.SessionStateService.ClearSession();'''

count3 = content.count(old3)
print(f"Fix 3 (ClearSession on logout): {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("Fix 3 OK")
else:
    print("Fix 3 NOT FOUND")

open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print("DONE")
