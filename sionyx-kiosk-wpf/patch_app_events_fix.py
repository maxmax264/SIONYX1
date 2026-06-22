import sys

path = r"src\SionyxKiosk\App.xaml.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the current event subscription with a clean single-registration version
old = '''        // Subscribe to update progress events
        Services.AutoUpdateService.UpdateStarted += (version) =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                var win = new Views.Windows.UpdateProgressWindow();
                win.SetVersion(version);
                win.Show();
                MainWindow = win;
            });
        };

        Services.AutoUpdateService.ProgressChanged += (percent, status) =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                if (MainWindow is Views.Windows.UpdateProgressWindow win)
                    win.SetProgress(percent, status);
            });
        };

        Services.AutoUpdateService.UpdateCompleted += () =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                if (MainWindow is Views.Windows.UpdateProgressWindow win)
                    win.SetComplete();
            });
        };'''

new = '''        // Subscribe to update progress events (single registration)
        Views.Windows.UpdateProgressWindow? _updateWin = null;

        Services.AutoUpdateService.UpdateStarted += (version) =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                if (_updateWin != null) return; // already showing
                _updateWin = new Views.Windows.UpdateProgressWindow();
                _updateWin.SetVersion(version);
                _updateWin.Show();
                MainWindow = _updateWin;
            });
        };

        Services.AutoUpdateService.ProgressChanged += (percent, status) =>
        {
            Current.Dispatcher.Invoke(() => _updateWin?.SetProgress(percent, status));
        };

        Services.AutoUpdateService.UpdateCompleted += () =>
        {
            Current.Dispatcher.Invoke(() =>
            {
                _updateWin?.SetComplete();
                _updateWin = null;
            });
        };'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("App.xaml.cs patched successfully!")
