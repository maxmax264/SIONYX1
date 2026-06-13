content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()
idx = content.find('MessagesPage(')
print(content[idx-100:idx+200])
