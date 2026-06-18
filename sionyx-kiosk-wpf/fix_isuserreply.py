path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs'
content = open(path, encoding='utf-8').read()

old = 'var isUserReply = msg.TryGetValue("isUserReply", out var iur) && iur is bool ur && ur;'
new = 'var isUserReply = msg.TryGetValue("isUserReply", out var iur) && (iur is bool ur && ur || iur?.ToString()?.ToLower() == "true");'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
