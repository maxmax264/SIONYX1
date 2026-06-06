content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KeyboardRestrictionService.cs', encoding='utf-8').read()
old = '''    public void Stop()
    {
        if (_hookHandle != IntPtr.Zero)
        {
            Logger.Information("Stopping keyboard restriction service");
            UnhookWindowsHookEx(_hookHandle);
            _hookHandle = IntPtr.Zero;
        }
    }'''
new = '''    public void Stop()
    {
        if (_hookHandle != IntPtr.Zero)
        {
            Logger.Information("Stopping keyboard restriction service");
            UnhookWindowsHookEx(_hookHandle);
            _hookHandle = IntPtr.Zero;
        }
        if (_hookThreadId != 0)
        {
            PostThreadMessage(_hookThreadId, 0x0012, IntPtr.Zero, IntPtr.Zero); // WM_QUIT
            _hookThreadId = 0;
        }
    }'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KeyboardRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
