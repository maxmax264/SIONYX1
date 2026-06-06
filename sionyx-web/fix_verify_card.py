content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()
old = "                  <Text\n                    style={{\n                      direction: 'ltr',\n                      display: 'inline-block',\n                      color: '#374151',\n                      fontSize: 13,\n                    }}\n                  >\n                    {userRecord.phoneNumber}\n                  </Text>"
new = """                  <Text
                    style={{
                      direction: 'ltr',
                      display: 'inline-block',
                      color: '#374151',
                      fontSize: 13,
                    }}
                  >
                    {userRecord.phoneNumber}
                  </Text>
                  {userRecord.phoneVerified ? (
                    <span style={{ color: '#52c41a', fontSize: 12 }}>\u2705</span>
                  ) : (
                    <span style={{ color: '#ff4d4f', fontSize: 12 }}>\u274c</span>
                  )}"""
count = content.count(old)
print(f"match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
