content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('class KioskMe')
print(content[idx:idx+400])
