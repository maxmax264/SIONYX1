content = open(r'.\src\SionyxKiosk\Services\ChatService.cs', encoding='utf-8').read()
old = '''            if (toUser == _userId && !isRead)'''
new = '''            if (toUser == _userId)'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ChatService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
