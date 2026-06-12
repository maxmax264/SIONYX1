content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = "  const filteredMessages = selectedUserId\n    ? messages.filter(m => m.toUserId === selectedUserId)\n    : messages;"

new = "  const filteredMessages = (selectedUserId\n    ? messages.filter(m => m.toUserId === selectedUserId)\n    : messages).filter(m => !deletedIds.includes(m.id));"

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
