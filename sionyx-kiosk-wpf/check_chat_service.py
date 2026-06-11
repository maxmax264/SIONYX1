content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', encoding='utf-8').read()
idx = content.find('fromUserId === userId')
print(repr(content[idx-100:idx+200]))
