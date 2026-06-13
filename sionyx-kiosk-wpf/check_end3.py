content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
idx = content.find('#F0FDF4')
print(repr(content[idx+3200:idx+3800]))
