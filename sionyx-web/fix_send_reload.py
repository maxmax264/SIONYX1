content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """        const msgResult = await getMessagesForUser(orgId, selectedUser.uid);
        if (msgResult.success) {
          const sorted = [...msgResult.messages].sort(
            (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
          );
          setUserMessages(sorted);
        }"""
new = """        const [msgResult2, repliesResult2] = await Promise.all([
          getMessagesForUser(orgId, selectedUser.uid),
          getUserReplies(orgId, selectedUser.uid),
        ]);
        const msgs2 = msgResult2.success ? msgResult2.messages : [];
        const replies2 = repliesResult2.success ? repliesResult2.replies : [];
        const merged2 = [...msgs2, ...replies2].sort(
          (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
        );
        setUserMessages(merged2);"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
