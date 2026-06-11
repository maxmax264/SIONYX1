content = open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
old = """                      {msg.fromSupervisor && (
                        <Tag color='blue' style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>מפקח</Tag>
                      )}"""
new = """                      {msg.fromSupervisor && (
                        <Tag color='blue' style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>מפקח</Tag>
                      )}
                      {msg.isReply && (
                        <Tag color='green' style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>תגובת לקוח</Tag>
                      )}"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
