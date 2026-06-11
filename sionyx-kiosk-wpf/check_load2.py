content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('private async Task LoadMessagesAsync()')
print(content[idx+3000:idx+6000])
