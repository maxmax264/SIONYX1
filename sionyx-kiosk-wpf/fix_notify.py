content = open(r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs', encoding='utf-8').read()
old = """    private void OnMessagesReceived(List<Dictionary<string, object?>> msgs)
    {
        var count = msgs.Count;
        Application.Current?.Dispatcher.BeginInvoke(() =>
        {
            var isNew = UnreadMessages == 0 && count > 0;
            UnreadMessages = count;
            if (isNew)
                NewMessageReceived?.Invoke();
        });
    }"""
new = """    private void OnMessagesReceived(List<Dictionary<string, object?>> msgs)
    {
        var count = msgs.Count;
        Application.Current?.Dispatcher.BeginInvoke(() =>
        {
            var isNew = count > UnreadMessages;
            UnreadMessages = count;
            if (isNew)
                NewMessageReceived?.Invoke();
        });
    }"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
