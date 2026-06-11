content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()

# Fix pos 3694 - openChat sort
old1 = "      const merged "
# need more context
idx = content.find("getUserReplies(orgId, userItem.uid),\n      ]);\n      const msgs = msgsResult.success ? msgsResult.messages : [];\n      const replies = repliesResult.success ? repliesResult.replies : [];\n      const merged")
print(f"idx1: {idx}")
print(repr(content[idx+150:idx+300]))
