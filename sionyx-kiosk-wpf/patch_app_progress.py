import sys

path = r"src\SionyxKiosk\App.xaml.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Subscribe to update events after the update check call
old = '''        // Check for updates in background (non-blocking)
        _ = Task.Run(async () =>
        {
            try
            {
                var version = GetVersion();
                await Services.AutoUpdateService.CheckAndUpdateAsync(version);
            }
            catch (Exception ex) { Log.Warning(ex, "[Update] Background update check failed"); }
        });'''

new = '''        // Subscribe to update progress events
        Services.AutoUpdateService.UpdateStarted += (version) =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                var win = new Views.Windows.UpdateProgressWindow();
                win.SetVersion(version);
                win.Show();
                MainWindow = win;

                Services.AutoUpdateService.ProgressChanged += (percent, status) =>
                    win.SetProgress(percent, status);

                Services.AutoUpdateService.UpdateCompleted += () =>
                {
                    win.SetComplete();
                };
            });
        };

        // Check for updates in background (non-blocking)
        _ = Task.Run(async () =>
        {
            try
            {
                var version = GetVersion();
                await Services.AutoUpdateService.CheckAndUpdateAsync(version);
            }
            catch (Exception ex) { Log.Warning(ex, "[Update] Background update check failed"); }
        });'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
