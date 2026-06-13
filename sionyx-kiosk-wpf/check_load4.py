content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('private async Task LoadMessagesAsync')
print(repr(content[idx-5:idx+45]))
