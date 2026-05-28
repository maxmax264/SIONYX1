content = open(r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs', encoding='utf-8').read()

old = '''    private void OnTimeUpdated(int remaining)
    {
        var ts = TimeSpan.FromSeconds(Math.Max(0, remaining));
        RemainingTime = ts.ToString(@"hh\:mm\:ss");
    }'''
new = '''    private void OnTimeUpdated(int remaining)
    {
        Application.Current?.Dispatcher.BeginInvoke(() =>
        {
            var ts = TimeSpan.FromSeconds(Math.Max(0, remaining));
            RemainingTime = ts.ToString(@"hh\:mm\:ss");
        });
    }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
