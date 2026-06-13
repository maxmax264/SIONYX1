content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
idx = content.find('_deletedIds')
if idx == -1:
    print('No deletedIds yet')
else:
    print(content[idx-100:idx+200])
