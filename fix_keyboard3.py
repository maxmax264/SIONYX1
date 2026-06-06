content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KeyboardRestrictionService.cs', encoding='utf-8').read()
old = '''        _hookThread = new Thread(RunHookLoop) { IsBackground = true, Name = "KeyboardHook" };
        _hookThread.Start();'''
new = '''        _hookThread = new Thread(RunHookLoop) { IsBackground = true, Name = "KeyboardHook" };
        _hookThread.Start();
        // Give thread time to register its ID
        Thread.Sleep(100);'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KeyboardRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
