content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old1 = '        ShowAuthWindow();\n    }\n\n    // =================='
new1 = '''        // Check for stale session from power outage
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
        }

        ShowAuthWindow();
    }

    // =================='''

count1 = content.count(old1)
print(f"Fix 1: {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
