content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''    [ObservableProperty] private string _backgroundImageUrl = "";
    [ObservableProperty] private bool _hasBackgroundImage;
    [ObservableProperty] private double _bgOpacity = 0.55;
    [ObservableProperty] private string _bgStretch = "UniformToFill";
    [ObservableProperty] private System.Windows.Media.ImageSource? _backgroundImageSource;'''

new = '''    [ObservableProperty] private string _backgroundImageUrl = "";
    [ObservableProperty] private bool _hasBackgroundImage;
    [ObservableProperty] private double _bgOpacity = 0.55;
    [ObservableProperty] private string _bgStretch = "UniformToFill";
    [ObservableProperty] private System.Windows.Media.ImageSource? _backgroundImageSource;

    // authDesign properties
    [ObservableProperty] private string _overlayColor1 = "#6366F1";
    [ObservableProperty] private string _overlayColor2 = "#8B5CF6";
    [ObservableProperty] private string _brandSubtitle = "ניהול מחשבים חכם";
    [ObservableProperty] private string _welcomeText = "ברוכים הבאים";
    [ObservableProperty] private string _welcomeSubtext = "התחבר לחשבון שלך";
    [ObservableProperty] private bool _showRegister = true;
    [ObservableProperty] private bool _cleanMode = false;
    [ObservableProperty] private System.Windows.Media.Brush _overlayGradient = new System.Windows.Media.LinearGradientBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"),
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#8B5CF6"),
        45);'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
