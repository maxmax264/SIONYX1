content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()

old = """    const replies = Object.entries(snap.val()).map(([id, r]) => ({
      id, ...r, isReply: true, fromSupervisorReply: r.fromSupervisorReply || false,
    }));"""

new = """    const replies = Object.entries(snap.val())
      .filter(([, r]) => r.fromSupervisorReply === true)
      .map(([id, r]) => ({ id, ...r, isReply: true }));"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
