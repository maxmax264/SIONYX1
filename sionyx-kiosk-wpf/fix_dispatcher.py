content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = """    private void UpdateAdminUI()
    {
        AdminLoadingPanel.Visibility = Visibility.Collapsed;
        if (_adminMessages.Count == 0)
        {
            AdminEmptyPanel.Visibility = Visibility.Visible;
            AdminScroll.Visibility = Visibility.Collapsed;
        }
        else
        {
            AdminEmptyPanel.Visibility = Visibility.Collapsed;
            AdminScroll.Visibility = Visibility.Visible;
            AdminMessagesList.ItemsSource = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
            AdminScroll.ScrollToEnd();
        }
    }

    private void UpdateSupervisorUI()
    {
        SupervisorLoadingPanel.Visibility = Visibility.Collapsed;
        if (_supervisorMessages.Count == 0)
        {
            SupervisorEmptyPanel.Visibility = Visibility.Visible;
            SupervisorScroll.Visibility = Visibility.Collapsed;
        }
        else
        {
            SupervisorEmptyPanel.Visibility = Visibility.Collapsed;
            SupervisorScroll.Visibility = Visibility.Visible;
            SupervisorMessagesList.ItemsSource = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();
            SupervisorScroll.ScrollToEnd();
        }
    }"""
new = """    private void UpdateAdminUI()
    {
        Dispatcher.Invoke(() =>
        {
            AdminLoadingPanel.Visibility = Visibility.Collapsed;
            if (_adminMessages.Count == 0)
            {
                AdminEmptyPanel.Visibility = Visibility.Visible;
                AdminScroll.Visibility = Visibility.Collapsed;
            }
            else
            {
                AdminEmptyPanel.Visibility = Visibility.Collapsed;
                AdminScroll.Visibility = Visibility.Visible;
                AdminMessagesList.ItemsSource = _adminMessages.OrderBy(m => m.RawTimestamp).ToList();
                AdminScroll.ScrollToEnd();
            }
        });
    }

    private void UpdateSupervisorUI()
    {
        Dispatcher.Invoke(() =>
        {
            SupervisorLoadingPanel.Visibility = Visibility.Collapsed;
            if (_supervisorMessages.Count == 0)
            {
                SupervisorEmptyPanel.Visibility = Visibility.Visible;
                SupervisorScroll.Visibility = Visibility.Collapsed;
            }
            else
            {
                SupervisorEmptyPanel.Visibility = Visibility.Collapsed;
                SupervisorScroll.Visibility = Visibility.Visible;
                SupervisorMessagesList.ItemsSource = _supervisorMessages.OrderBy(m => m.RawTimestamp).ToList();
                SupervisorScroll.ScrollToEnd();
            }
        });
    }"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
