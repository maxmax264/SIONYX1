content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('Logger')
print(content[idx-100:idx+200])
