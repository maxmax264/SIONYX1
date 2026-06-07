content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\HomePage.xaml.cs', encoding='utf-8').read()
old = '''    private void OnPageUnloaded(object sender, RoutedEventArgs e)
    {'''
new = '''    private void OnPageLoaded(object sender, RoutedEventArgs e)
    {
        Log.Debug("[HOME] HomePage.Loaded — re-subscribing events and refreshing");
        _vm.ViewMessagesRequested -= OpenMessageDialog;
        _vm.NavigateToPackagesRequested -= NavigateToPackages;
        _vm.SessionStartedSuccessfully -= OnSessionStarted;
        _vm.ResumeSessionRequested -= OnResumeSession;
        _vm.ViewMessagesRequested += OpenMessageDialog;
        _vm.NavigateToPackagesRequested += NavigateToPackages;
        _vm.SessionStartedSuccessfully += OnSessionStarted;
        _vm.ResumeSessionRequested += OnResumeSession;
        UpdateMessageCard(_vm.UnreadMessages);
        UpdateAnnouncementsSection();
    }

    private void OnPageUnloaded(object sender, RoutedEventArgs e)
    {'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\HomePage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
