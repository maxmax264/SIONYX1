content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('FloatingNotification.Show')
print(repr(content[idx-50:idx+300]))
