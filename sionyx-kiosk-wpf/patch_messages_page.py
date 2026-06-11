content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()

old_unsub = """    const unsubMessages = subscribeToMessages(orgId, data => {
      setMessages(data);
      setLoading(false);
    });
    const unsubUsers = subscribeToUsers(orgId, data => {
      setUsers(data);
      setLoading(false);
    });
    return () => {
      unsubMessages();
      unsubUsers();
    };"""

new_unsub = """    const unsubMessages = subscribeToMessages(orgId, data => {
      setMessages(data);
      setLoading(false);
    });
    const unsubUsers = subscribeToUsers(orgId, data => {
      setUsers(data);
      setLoading(false);
    });
    const unsubReplies = subscribeToUserReplies(orgId, data => {
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

count = content.count(old_unsub)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old_unsub, new_unsub, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
