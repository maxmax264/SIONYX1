content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
idx = content.find('ItemTemplate')
print(content[idx:idx+3000])
