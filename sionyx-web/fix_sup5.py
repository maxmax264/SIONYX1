content = open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
old = """const msgsRes = await getOrgMessages(selectedOrgId);
      if (msgsRes.success) setMessages(msgsRes.messages || []);"""
new = """const [msgsRes2, repliesRes2] = await Promise.all([
        getOrgMessages(selectedOrgId),
        getOrgUserReplies(selectedOrgId),
      ]);
      const msgs2 = msgsRes2.success ? msgsRes2.messages || [] : [];
      const replies2 = repliesRes2.success ? repliesRes2.replies || [] : [];
      setMessages([...msgs2, ...replies2].sort((a, b) => b.timestamp - a.timestamp));"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
