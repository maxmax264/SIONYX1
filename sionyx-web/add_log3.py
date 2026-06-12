content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """    const res = isReply
      ? await deleteSupervisorReply(selectedOrgId, msg.id)
      : await deleteSupervisorMessage(selectedOrgId, msg.id);
    if (res.success) {"""

new = """    const res = isReply
      ? await deleteSupervisorReply(selectedOrgId, msg.id)
      : await deleteSupervisorMessage(selectedOrgId, msg.id);
    console.log('Delete result:', JSON.stringify(res));
    if (res.success) {"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
