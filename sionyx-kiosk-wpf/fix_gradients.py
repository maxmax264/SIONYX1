content = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''                // ׳¢׳"׳›׳ ׳׳× ׳"׳'׳¨׳"׳™׳׳ ׳˜
                try
                {
                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var col1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    var col2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(col1, col2, 45);
                }
                catch { }'''

new = '''                // עדכון הגרדיינט לפאנל הלוגו
                try
                {
                    var c1 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor1);
                    var c2 = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(OverlayColor2);
                    OverlayGradient = new System.Windows.Media.LinearGradientBrush(c1, c2, 45);
                }
                catch { }
                // עדכון צבע כפתור בנפרד
                try
                {
                    var btnCol = !string.IsNullOrEmpty(ButtonColor) ? ButtonColor : OverlayColor1;
                    var bc = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(btnCol);
                    ButtonGradient = new System.Windows.Media.SolidColorBrush(bc);
                }
                catch { }'''

count = content.count(old)
print(f'Found {count} matches')
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
