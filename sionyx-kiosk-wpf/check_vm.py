f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()
lines = c.split('\n')
for i, line in enumerate(lines):
    if any(x in line for x in ['TryGetProperty', 'ObservableProperty', 'OverlayGradient', 'ButtonColor', 'CleanMode', 'BrandName', 'WelcomeText', 'ShowRegister']):
        print(f'{i+1}: {line.strip()}')
