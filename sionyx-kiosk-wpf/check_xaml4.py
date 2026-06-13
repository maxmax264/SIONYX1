content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
idx = content.find('DisplayTime')
print(content[idx:idx+1000])
