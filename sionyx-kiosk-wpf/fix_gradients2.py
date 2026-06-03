f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = '''                try
                {
                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var col1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    var col2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(col1, col2, 45);
                }
                catch { }'''

new = '''                try
                {
                    var c1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor1);
                    var c2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor2);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(c1, c2, 45);
                }
                catch { }
                try
                {
                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var bc = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    ButtonGradient = new System.Windows.Media.SolidColorBrush(bc);
                }
                catch { }'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
