content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = 'var repliesResult = await _firebase.DbGetAsync($"organizations/{_firebase.OrgId}/userReplies");'
new = 'var repliesResult = await _firebase.DbGetAsync($"userReplies");'

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
