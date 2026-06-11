content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', encoding='utf-8').read()

old = """    snapshot.forEach(child => {
      const data = child.val();
      if (data.fromUserId === userId) {
        replies.push({ id: child.key, ...data, isReply: true });
      }
    });"""

new = """    snapshot.forEach(child => {
      const data = child.val();
      if (data.fromUserId === userId && !data.fromSupervisorReply) {
        replies.push({ id: child.key, ...data, isReply: true });
      }
    });"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
