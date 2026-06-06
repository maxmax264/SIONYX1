content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()
old = "                <Descriptions.Item label='\u05ea\u05e7\u05e6\u05d9\u05d1 \u05d4\u05d3\u05e4\u05e1\u05d5\u05ea'>"
new = """                <Descriptions.Item label='\u05d0\u05d9\u05de\u05d5\u05ea \u05d8\u05dc\u05e4\u05d5\u05df'>
                  {selectedUser.phoneVerified ? (
                    <Tag color='green' icon={<span>\u2705</span>}>\u05de\u05d0\u05d5\u05de\u05ea</Tag>
                  ) : (
                    <Space>
                      <Tag color='red' icon={<span>\u274c</span>}>\u05dc\u05d0 \u05de\u05d0\u05d5\u05de\u05ea</Tag>
                      <Button size='small' type='primary' onClick={() => handleVerifyPhone(selectedUser)}>
                        \u05d0\u05de\u05ea \u05d9\u05d3\u05e0\u05d9\u05ea
                      </Button>
                    </Space>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label='\u05ea\u05e7\u05e6\u05d9\u05d1 \u05d4\u05d3\u05e4\u05e1\u05d5\u05ea'>"""
count = content.count(old)
print(f"match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
