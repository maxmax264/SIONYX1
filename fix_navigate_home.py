with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8') as f:
    content = f.read()

old = '''        mainWindow.Show();
        MainWindow = mainWindow;
        Log.Information("MainWindow shown and set as Application.MainWindow");
        // Start system services
        StartSystemServices();'''

new = '''        mainWindow.Show();
        MainWindow = mainWindow;
        Log.Information("MainWindow shown and set as Application.MainWindow");
        // Navigate to Home explicitly (Loaded fires only on first Show)
        mainWindow.NavigateHome();
        // Start system services
        StartSystemServices();'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
