content = open(r'.\src\pages\OverviewPage.jsx', encoding='utf-8').read()

old = """                                  {u.currentComputerName && (
                                    <Text type='secondary' style={{ fontSize: 11 }}>
                                      <DesktopOutlined style={{ marginLeft: 4 }} />
                                      {u.currentComputerName}
                                    </Text>
                                  )}
                                </div>
                              </div>
                            </div>
                          </Card>"""

new = """                                  {u.currentComputerName && (
                                    <Text type='secondary' style={{ fontSize: 11 }}>
                                      <DesktopOutlined style={{ marginLeft: 4 }} />
                                      {u.currentComputerName}
                                    </Text>
                                  )}
                                  {u.remainingTime != null && (
                                    <Text style={{ fontSize: 11, color: u.remainingTime < 300 ? '#ef4444' : '#10b981', fontWeight: 600 }}>
                                      {'⏱ נשאר: ' + Math.floor(u.remainingTime / 60) + ' דק'}
                                    </Text>
                                  )}
                                  {u.sessionStartTime && (
                                    <Text type='secondary' style={{ fontSize: 11 }}>
                                      {'התחיל: ' + new Date(u.sessionStartTime).toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })}
                                    </Text>
                                  )}
                                </div>
                              </div>
                            </div>
                          </Card>"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\OverviewPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
