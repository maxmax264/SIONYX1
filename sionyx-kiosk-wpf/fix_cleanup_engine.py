content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''                var browserCleanup = _host!.Services.GetRequiredService<BrowserCleanupService>();
                        browserCleanup.CleanupWithBrowserClose();
                        browserCleanup.CleanupDownloads();
                        Services.SessionStateService.ClearSession();'''

new = '''                var browserCleanup = _host!.Services.GetRequiredService<BrowserCleanupService>();
                        // Only clean browser/downloads if user actually entered desktop
                        if (Services.SessionStateService.HasEnteredDesktop())
                        {
                            browserCleanup.CleanupWithBrowserClose();
                            browserCleanup.CleanupDownloads();
                        }
                        Services.SessionStateService.ClearSession();'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
