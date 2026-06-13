content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
idx = content.find('DataTemplate')
print(content[idx:idx+2000])
