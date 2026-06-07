with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8') as f:
    content = f.read()

old = '        mainWindow.Show();\n        MainWindow = mainWindow;\n        Log.Information("MainWindow shown and set as Application.MainWindow");\n\n        // Start system services\n        StartSystemServices();'

new = '        mainWindow.Show();\n        MainWindow = mainWindow;\n        Log.Information("MainWindow shown and set as Application.MainWindow");\n        // Navigate to Home explicitly (Loaded fires only on first Show)\n        mainWindow.NavigateHome();\n\n        // Start system services\n        StartSystemServices();'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
