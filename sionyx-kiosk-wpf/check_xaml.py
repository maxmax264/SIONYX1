f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
props = ['OverlayGradient', 'OverlayColor1', 'OverlayColor2', 'ButtonColor', 'CleanMode', 
         'BrandSubtitle', 'WelcomeText', 'WelcomeSubtext', 'ShowRegister', 'BgOpacity', 
         'BgStretch', 'HasBackgroundImage', 'BackgroundImageSource']
print('=== Properties ב-XAML ===')
for prop in props:
    count = c.count(prop)
    status = 'OK' if count > 0 else 'MISSING'
    print(f'{status} ({count}x): {prop}')
