content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """                    {/* Message bubble */}
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'flex-start',
                        marginBottom: 10,
                        alignItems: 'flex-start',
                        gap: 6,
                      }}
                    >
                      <div
                        style={{
                          maxWidth: '78%',
                          background: tokens.gradientPrimary,
                          color: '#fff',
                          padding: '11px 16px',
                          borderRadius: '18px 18px 6px 18px',
                          boxShadow: '0 2px 12px rgba(102, 126, 234, 0.2)',
                        }}
                      >"""
new = """                    {/* Message bubble */}
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: msg.isReply ? 'flex-end' : 'flex-start',
                        marginBottom: 10,
                        alignItems: 'flex-start',
                        gap: 6,
                      }}
                    >
                      <div
                        style={{
                          maxWidth: '78%',
                          background: msg.isReply ? '#e6f7e6' : tokens.gradientPrimary,
                          color: msg.isReply ? '#1a7f1a' : '#fff',
                          padding: '11px 16px',
                          borderRadius: msg.isReply ? '18px 18px 18px 6px' : '18px 18px 6px 18px',
                          boxShadow: msg.isReply ? '0 2px 8px rgba(0,0,0,0.08)' : '0 2px 12px rgba(102, 126, 234, 0.2)',
                        }}
                      >"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
