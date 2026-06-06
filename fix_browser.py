content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', encoding='utf-8').read()
old = '        "Cookies", "Cookies-journal", "Login Data", "Login Data-journal",\n        "Web Data", "Web Data-journal", "History", "History-journal",\n        "Sessions", "Current Session", "Current Tabs",\n        "Last Session", "Last Tabs",'
new = '        "Cookies", "Cookies-journal", "Login Data", "Login Data-journal",\n        "Web Data", "Web Data-journal", "History", "History-journal",\n        "Sessions", "Current Session", "Current Tabs",\n        "Last Session", "Last Tabs",\n        "Preferences", "Secure Preferences",'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\BrowserCleanupService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
