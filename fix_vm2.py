content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);
                    return;'''

new = '''                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);
                    await LoadAuthDesignAsync();
                    return;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
