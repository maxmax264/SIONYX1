content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = '            var result = await _chat.GetUnreadMessagesAsync(useCache: false);'
new = '            var result = await _chat.GetAllMessagesAsync();'
count = content.count(old)
print(f"Found {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
