content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()
old = '            if (toUser == _userId)'
new = '            if (toUser == _userId && !isRead)'
count = content.count(old)
print(f"Found {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
