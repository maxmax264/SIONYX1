content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('fromSupervisor')
print(content[idx-300:idx+200])
