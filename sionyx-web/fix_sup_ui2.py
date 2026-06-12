content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """                  <div style={{ display: 'flex', gap: 4, marginTop: 2 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Text style={{ fontSize: 13 }}>{msg.message}</Text>
                    <Button
                      type='text'
                      danger
                      size='small'
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(msg)}
                      style={{ marginRight: 8, flexShrink: 0 }}
                    />
                  </div>
                </div>
              </List.Item>
            )}"""

new = """                </div>
              </List.Item>
            );
          }}"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
