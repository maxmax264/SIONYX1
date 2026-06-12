content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('handleDeleteMessage')
while idx != -1:
    print(f"=== pos {idx} ===")
    print(content[idx-50:idx+400])
    print()
    idx = content.find('handleDeleteMessage', idx+1)
