content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('LoadMessagesAsync')
print(repr(content[idx-20:idx+40]))
