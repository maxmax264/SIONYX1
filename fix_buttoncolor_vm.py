f = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = '''                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = (c1.GetString() ?? "#6366F1").Trim();
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = (c2.GetString() ?? "#8B5CF6").Trim();'''

new = '''                if (d.TryGetProperty("overlayColor1", out var c1)) OverlayColor1 = (c1.GetString() ?? "#6366F1").Trim();
                if (d.TryGetProperty("overlayColor2", out var c2)) OverlayColor2 = (c2.GetString() ?? "#8B5CF6").Trim();
                if (d.TryGetProperty("buttonColor", out var bc)) { var bcStr = bc.GetString(); if (!string.IsNullOrEmpty(bcStr)) ButtonColor = bcStr.Trim(); }'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)

old2 = '''                    var col1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor1);
                    var col2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor2);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(col1, col2, 45);'''

new2 = '''                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var col1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    var col2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(col1, col2, 45);'''

count2 = c.count(old2)
print(f'Found {count2} matches')
if count2 == 1:
    c = c.replace(old2, new2, 1)

if count == 1 and count2 == 1:
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND - לא נשמר')
