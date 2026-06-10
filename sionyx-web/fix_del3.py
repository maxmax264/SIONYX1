content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """  const handleSendMessage = async () => {"""
new = """  const handleDeleteMessage = async (msgId) => {
    try {
      const result = await deleteMessage(orgId, msgId);
      if (result.success) {
        setUserMessages(prev => prev.filter(m => m.id !== msgId));
        setMessages(prev => prev.filter(m => m.id !== msgId));
        message.success('ההודעה נמחקה');
      } else {
        message.error('שגיאה במחיקה');
      }
    } catch (error) {
      message.error('שגיאה במחיקה');
    }
  };

  const handleSendMessage = async () => {"""
count = content.count(old)
print(f"handler: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
