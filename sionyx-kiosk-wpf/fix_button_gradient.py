content = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''    [ObservableProperty] private System.Windows.Media.Brush _overlayGradient = new System.Windows.Media.LinearGradientBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"),
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#8B5CF6"),
        45);'''

new = '''    [ObservableProperty] private System.Windows.Media.Brush _overlayGradient = new System.Windows.Media.LinearGradientBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"),
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#8B5CF6"),
        45);
    [ObservableProperty] private System.Windows.Media.Brush _buttonGradient = new System.Windows.Media.SolidColorBrush(
        (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#6366F1"));'''

count = content.count(old)
print(f'Found {count} matches')
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
