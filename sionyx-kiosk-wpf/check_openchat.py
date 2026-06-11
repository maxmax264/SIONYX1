content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('getUserReplies')
print(repr(content[idx-100:idx+400]))
