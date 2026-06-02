content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '                if (d.TryGetProperty("cleanMode", out var cm)) CleanMode = cm.GetBoolean();'
new = '''                if (d.TryGetProperty("cleanMode", out var cm)) CleanMode = cm.GetBoolean();
                if (d.TryGetProperty("formX", out var fx)) FormX = fx.GetDouble();
                if (d.TryGetProperty("formY", out var fy)) FormY = fy.GetDouble();
                if (d.TryGetProperty("formWidth", out var fw)) FormWidth = fw.GetDouble();'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
