content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
print('YES' if 'Load user replies from Firebase' in content else 'NO')
