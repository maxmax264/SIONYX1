content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()

# 1. Remove subscribeToUserReplies from main useEffect
old_unsub = """    const unsubReplies = subscribeToUserReplies(orgId, data => {
      setMessages(prev => {
        const withoutReplies = prev.filter(m => !m.isReply);
        return [...withoutReplies, ...data];
      });
    });
    return () => {
      unsubMessages();
      unsubUsers();
      unsubReplies();
    };"""

new_unsub = """    return () => {
      unsubMessages();
      unsubUsers();
    };"""

count = content.count(old_unsub)
print(f"Found main unsub: {count}")
if count == 1:
    content = content.replace(old_unsub, new_unsub, 1)
    print('Removed from main useEffect')

# 2. Fix openChat to also subscribe to replies for the specific user
old_openchat = """        const [msgsResult, repliesResult] = await Promise.all([
          getMessagesForUser(orgId, userItem.uid),
          getUserReplies(orgId, userItem.uid),
        ]);
        const msgs = msgsResult.success ? msgsResult.messages : [];
        const replies = repliesResult.success ? repliesResult.replies : [];
        const merged = [...msgs, ...replies].sort(
          (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
        );
        setUserMessages(merged);"""

new_openchat = """        const [msgsResult, repliesResult] = await Promise.all([
          getMessagesForUser(orgId, userItem.uid),
          getUserReplies(orgId, userItem.uid),
        ]);
        const msgs = msgsResult.success ? msgsResult.messages : [];
        const replies = repliesResult.success ? repliesResult.replies : [];
        const merged = [...msgs, ...replies].sort(
          (a, b) => (a.timestamp || 0) - (b.timestamp || 0)
        );
        setUserMessages(merged);"""

count2 = content.count(old_openchat)
print(f"Found openChat: {count2}")
if count2 == 1:
    content = content.replace(old_openchat, new_openchat, 1)
    print('Fixed openChat sort')

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
print('Done')
