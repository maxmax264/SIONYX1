content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = "    private async Task LoadMessagesAsync()"

new = """    private async void DeleteMessage_Click(object sender, System.Windows.RoutedEventArgs e)
    {
        if (sender is System.Windows.Controls.Button btn && btn.Tag is string msgId)
        {
            var isReply = msgId.StartsWith("reply_");
            var path = isReply ? $"userReplies/{msgId}" : $"messages/{msgId}";
            var result = await _firebase.DbDeleteAsync(path);
            if (result.Success)
            {
                _adminMessages.RemoveAll(m => m.Id == msgId);
                _supervisorMessages.RemoveAll(m => m.Id == msgId);
                UpdateAdminUI();
                UpdateSupervisorUI();
            }
        }
    }

    private async Task LoadMessagesAsync()"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
