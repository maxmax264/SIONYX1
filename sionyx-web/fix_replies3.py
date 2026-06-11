content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """  const openChat = async userItem => {
    setSelectedUser(userItem);
    setChatVisible(true);
    setLoadingChat(true);

    try {
      const result = await getMessagesForUser(orgId, userItem.uid);
      if (result.success) {
        const sorted = [...result.messages].sort(
          (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
        );
        setUserMessages(sorted);
      }
    } catch (error) {
      logger.error('Error loading chat:', error);
      message.error('שגיאה בטעינת ההודעות');
    } finally {
      setLoadingChat(false);
    }
  };"""
new = """  const openChat = async userItem => {
    setSelectedUser(userItem);
    setChatVisible(true);
    setLoadingChat(true);

    try {
      const [msgsResult, repliesResult] = await Promise.all([
        getMessagesForUser(orgId, userItem.uid),
        getUserReplies(orgId, userItem.uid),
      ]);
      const msgs = msgsResult.success ? msgsResult.messages : [];
      const replies = repliesResult.success ? repliesResult.replies : [];
      const merged = [...msgs, ...replies].sort(
        (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
      );
      setUserMessages(merged);
    } catch (error) {
      logger.error('Error loading chat:', error);
      message.error('שגיאה בטעינת ההודעות');
    } finally {
      setLoadingChat(false);
    }
  };"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
