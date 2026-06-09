content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '                        _host!.Services.GetRequiredService<BrowserCleanupService>().CleanupWithBrowserClose();\n                    }'
new = '                        var browserCleanup = _host!.Services.GetRequiredService<BrowserCleanupService>();\n                        browserCleanup.CleanupWithBrowserClose();\n                        browserCleanup.CleanupDownloads();\n                    }'
assert content.count(old) == 1, "not found: " + str(content.count(old))
content = content.replace(old, new)
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
print('OK')
