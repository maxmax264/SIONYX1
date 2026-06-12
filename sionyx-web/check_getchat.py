content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('getMessagesForUser')
while idx != -1:
    print(f"=== pos {idx} ===")
    print(content[idx-200:idx+300])
    print()
    idx = content.find('getMessagesForUser', idx+1)
