path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

old = 'Title="הודעות" FlowDirection="RightToLeft">'
new = 'Title="הודעות">'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
