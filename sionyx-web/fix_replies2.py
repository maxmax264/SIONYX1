content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """  getAllMessages,
  getMessagesForUser,
  sendMessage,
  deleteMessage,
  isUserActive,
  cleanupOldMessages,
} from '../services/chatService';"""
new = """  getAllMessages,
  getMessagesForUser,
  sendMessage,
  deleteMessage,
  getUserReplies,
  isUserActive,
  cleanupOldMessages,
} from '../services/chatService';"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
