content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('private async Task LoadMessagesAsync()')
print(content[idx:idx+500])
