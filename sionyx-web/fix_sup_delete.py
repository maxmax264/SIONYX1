content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

# Add DeleteOutlined to imports
old = "  CheckCircleOutlined,"
new = "  CheckCircleOutlined,\n  DeleteOutlined,"

content = content.replace(old, new, 1)

# Add deleteMessage/deleteUserReply imports
old = "import { getOrgMessages, sendSupervisorMessage, getOrgUserReplies } from '../services/supervisorMessageService';"
new = "import { getOrgMessages, sendSupervisorMessage, getOrgUserReplies, deleteSupervisorMessage, deleteSupervisorReply } from '../services/supervisorMessageService';"

content = content.replace(old, new, 1)

# Add handleDelete function before getUserName
old = "  const getUserName = userId => {"
new = """  const handleDelete = async (msg) => {
    const isReply = msg.id.startsWith('reply_');
    const res = isReply
      ? await deleteSupervisorReply(selectedOrgId, msg.id)
      : await deleteSupervisorMessage(selectedOrgId, msg.id);
    if (res.success) {
      setMessages(prev => prev.filter(m => m.id !== msg.id));
      antMsg.success('ההודעה נמחקה');
    } else {
      antMsg.error('שגיאה במחיקה');
    }
  };

  const getUserName = userId => {"""

content = content.replace(old, new, 1)

# Add delete button in list item
old = "                  <Text style={{ fontSize: 13 }}>{msg.message}</Text>"
new = """                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Text style={{ fontSize: 13 }}>{msg.message}</Text>
                    <Button
                      type='text'
                      danger
                      size='small'
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(msg)}
                      style={{ marginRight: 8, flexShrink: 0 }}
                    />
                  </div>"""

content = content.replace(old, new, 1)

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
print('Done')
