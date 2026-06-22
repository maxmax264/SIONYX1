import sys

path = r"src\SionyxKiosk\App.xaml.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''        // Subscribe to update progress events
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
        };'''

new = '''        // Subscribe to update progress events
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

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
