content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('UpdateAdminUI();')
print(repr(content[idx-200:idx+50]))
