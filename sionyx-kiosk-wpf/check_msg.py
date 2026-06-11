content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('subscribeToMessages')
# find the useEffect block
idx2 = content.find('subscribeToMessages(orgId')
print(repr(content[idx2-50:idx2+400]))
