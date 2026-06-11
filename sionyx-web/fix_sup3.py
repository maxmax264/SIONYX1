content = open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
old = """      const [usersRes, msgsRes] = await Promise.all([
        getOrgUsers(selectedOrgId),
        getOrgMessages(selectedOrgId),
      ]);
      if (usersRes.success) setUsers(usersRes.users || []);
      if (msgsRes.success) setMessages(msgsRes.messages || []);"""
new = """      const [usersRes, msgsRes, repliesRes] = await Promise.all([
        getOrgUsers(selectedOrgId),
        getOrgMessages(selectedOrgId),
        getOrgUserReplies(selectedOrgId),
      ]);
      if (usersRes.success) setUsers(usersRes.users || []);
      const msgs = msgsRes.success ? msgsRes.messages || [] : [];
      const replies = repliesRes.success ? repliesRes.replies || [] : [];
      const merged = [...msgs, ...replies].sort((a, b) => b.timestamp - a.timestamp);
      setMessages(merged);"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
