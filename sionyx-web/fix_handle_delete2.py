content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """  const handleDelete = async (msg) => {
    console.log('Delete msg:', msg.id, 'isReply:', msg.id.startsWith('reply_'));
    const isReply = msg.id.startsWith('reply_');
    const res = isReply
      ? await deleteSupervisorReply(selectedOrgId, msg.id)
      : await deleteSupervisorMessage(selectedOrgId, msg.id);
    console.log('Delete result:', JSON.stringify(res));
    if (res.success) {
      setMessages(prev => prev.filter(m => m.id !== msg.id));
      antMsg.success('ההודעה נמחקה');
    } else {
      antMsg.error('שגיאה במחיקה');
    }
  };"""

new = """  const handleDelete = async (msg) => {
    const newDeleted = [...deletedIds, msg.id];
    setDeletedIds(newDeleted);
    localStorage.setItem('sup_deleted_ids', JSON.stringify(newDeleted));
    setMessages(prev => prev.filter(m => m.id !== msg.id));
    antMsg.success('ההודעה נמחקה');
  };"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
