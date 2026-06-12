content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()

old = """  const handleDeleteMessage = async (msgId) => {
    try {
      console.log('Deleting message:', orgId, msgId);
      const result = await deleteMessage(orgId, msgId);
      console.log('Delete result:', JSON.stringify(result));
      if (result.success) {
        setUserMessages(prev => prev.filter(m => m.id !== msgId));
        setMessages(prev => prev.filter(m => m.id !== msgId));
        message.success('ההודעה נמחקה');
      } else {
        message.error('שגיאה במחיקה');
      }"""

new = """  const handleDeleteMessage = async (msgId) => {
    try {
      const isReply = msgId.startsWith('reply_');
      const result = isReply
        ? await deleteUserReply(orgId, msgId)
        : await deleteMessage(orgId, msgId);
      if (result.success) {
        setUserMessages(prev => prev.filter(m => m.id !== msgId));
        setMessages(prev => prev.filter(m => m.id !== msgId));
        message.success('ההודעה נמחקה');
      } else {
        message.error('שגיאה במחיקה');
      }"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
