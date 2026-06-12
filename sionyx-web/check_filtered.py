content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('filteredMessages')
while idx != -1:
    print(f"=== pos {idx} ===")
    print(content[idx-50:idx+200])
    print()
    idx = content.find('filteredMessages', idx+1)
    if idx > 10000:
        break
