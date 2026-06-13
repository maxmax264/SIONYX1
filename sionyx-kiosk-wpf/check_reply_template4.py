content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
idx = content.find('#F0FDF4')
print(content[idx+2500:idx+3500])
