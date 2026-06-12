content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\realtimeService.js', encoding='utf-8').read()

old = "        const messageList = Object.keys(messages).map(id => ({ id, ...messages[id] }));"
new = "        const messageList = Object.keys(messages).map(id => ({ id, ...messages[id] })).filter(m => !m.fromSupervisor);"

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\realtimeService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
