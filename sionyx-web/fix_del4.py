content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """                    {/* Message bubble */}
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'flex-start',
                        marginBottom: 10,
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
                      >
                        <div
                          style={{
                            fontSize: 14,
                            lineHeight: 1.6,
                            fontWeight: 400,
                            letterSpacing: '0.01em',
                          }}
                        >
                          {msg.message}
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'flex-end',
                            gap: 5,
                            marginTop: 5,
                            fontSize: 10,
                            opacity: 0.75,
                          }}
                        >
                          <span>{dayjs(msg.timestamp).format('HH:mm')}</span>
                          {msg.read ? (
                            <CheckCircleOutlined style={{ fontSize: 11, color: '#a3f0b5' }} />
                          ) : (
                            <ClockCircleOutlined style={{ fontSize: 11 }} />
                          )}
                        </div>
                      </div>
                    </div>"""
new = """                    {/* Message bubble */}
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
                      >
                        <div
                          style={{
                            fontSize: 14,
                            lineHeight: 1.6,
                            fontWeight: 400,
                            letterSpacing: '0.01em',
                          }}
                        >
                          {msg.message}
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'flex-end',
                            gap: 5,
                            marginTop: 5,
                            fontSize: 10,
                            opacity: 0.75,
                          }}
                        >
                          <span>{dayjs(msg.timestamp).format('HH:mm')}</span>
                          {msg.read ? (
                            <CheckCircleOutlined style={{ fontSize: 11, color: '#a3f0b5' }} />
                          ) : (
                            <ClockCircleOutlined style={{ fontSize: 11 }} />
                          )}
                        </div>
                      </div>
                      <Tooltip title="מחק הודעה">
                        <button
                          onClick={() => handleDeleteMessage(msg.id)}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '4px',
                            color: '#ccc',
                            display: 'flex',
                            alignItems: 'center',
                            marginTop: 4,
                            borderRadius: 4,
                            transition: 'color 0.2s',
                          }}
                          onMouseEnter={e => e.currentTarget.style.color = '#ff4d4f'}
                          onMouseLeave={e => e.currentTarget.style.color = '#ccc'}
                        >
                          <DeleteOutlined style={{ fontSize: 13 }} />
                        </button>
                      </Tooltip>
                    </div>"""
count = content.count(old)
print(f"bubble: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
