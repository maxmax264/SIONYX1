content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

# תיקון 1: ניקוי \n מהצבעים לפני ColorConverter
old = '''                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = c1.GetString() ?? "#6366F1";
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = c2.GetString() ?? "#8B5CF6";'''
new = '''                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = (c1.GetString() ?? "#6366F1").Trim();
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = (c2.GetString() ?? "#8B5CF6").Trim();'''

if old in content:
    content = content.replace(old, new)
    print("Fix1 LF: OK")
else:
    old2 = old.replace('\n', '\r\n')
    new2 = new.replace('\n', '\r\n')
    if old2 in content:
        content = content.replace(old2, new2)
        print("Fix1 CRLF: OK")
    else:
        print("Fix1: NOT FOUND")

open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
