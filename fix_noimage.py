content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''        BackgroundImageUrl = "";
        HasBackgroundImage = false;
        Serilog.Log.Warning("[BG] No background set");'''

new = '''        BackgroundImageUrl = "";
        HasBackgroundImage = false;
        Serilog.Log.Warning("[BG] No background set");
        await LoadAuthDesignAsync();'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
