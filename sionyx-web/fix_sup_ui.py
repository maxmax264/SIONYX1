content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """renderItem={msg => (
              <List.Item
                style={{ padding: '12px 16px', borderBottom: `1px solid ${token.colorBorderSecondary}` }}
              >
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <Space size={4}>
                      <UserOutlined style={{ color: token.colorTextTertiary }} />
                      <Text strong style={{ fontSize: 13 }}>
                        {getUserName(msg.toUserId)}
                      </Text>
                      {msg.fromSupervisor && (
                        <Tag color='blue' style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>מפקח</Tag>
                      )}
                      {msg.isReply && (
                        <Tag color='green' style={{ fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>תגובת לקוח</Tag>
                      )}
                    </Space>
                    <Space size={8}>
                      {msg.read ? (
                        <CheckCircleOutlined style={{ color: token.colorSuccess, fontSize: 12 }} />
                      ) : (
                        <Badge status='processing' />
                      )}
                      <Text type='secondary' style={{ fontSize: 11 }}>
                        {dayjs(msg.timestamp).fromNow()}
                      </Text>
                    </Space>
                  </div>"""

new = """renderItem={msg => {
                const isMine = msg.fromSupervisor;
                return (
              <List.Item style={{ padding: '6px 16px', border: 'none', justifyContent: isMine ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '70%', display: 'flex', flexDirection: 'column', alignItems: isMine ? 'flex-end' : 'flex-start' }}>
                  <Text type='secondary' style={{ fontSize: 11, marginBottom: 2 }}>
                    {isMine ? 'פיקוח' : getUserName(msg.toUserId)} · {dayjs(msg.timestamp).fromNow()}
                  </Text>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexDirection: isMine ? 'row' : 'row-reverse' }}>
                    <Button type='text' danger size='small' icon={<DeleteOutlined />} onClick={() => handleDelete(msg)} />
                    <div style={{
                      background: isMine ? token.colorPrimary : token.colorBgContainer,
                      color: isMine ? '#fff' : token.colorText,
                      border: isMine ? 'none' : `1px solid ${token.colorBorderSecondary}`,
                      borderRadius: 12,
                      padding: '8px 12px',
                      fontSize: 13,
                    }}>
                      {msg.message}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 4, marginTop: 2 }}>"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
