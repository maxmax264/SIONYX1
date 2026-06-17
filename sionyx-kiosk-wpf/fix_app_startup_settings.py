content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''                            _trayIcon.SettingsRequested += () =>
                            {
                                var dlg = new Views.Dialogs.SettingsDialog();
                                dlg.Show();
                            };'''

new = '''                            _trayIcon.SettingsRequested += () =>
                            {
                                var dlg = new Views.Dialogs.SettingsDialog();
                                dlg.Show();
                            };
                            _trayIcon.StartupSettingsRequested += () =>
                            {
                                var dlg = new Views.Dialogs.StartupSettingsDialog();
                                dlg.Show();
                            };'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
