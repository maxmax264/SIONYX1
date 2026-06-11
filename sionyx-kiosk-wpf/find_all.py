content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = 0
while True:
    idx = content.find('getUserReplies', idx)
    if idx == -1:
        break
    print(f"pos {idx}:")
    print(repr(content[idx-50:idx+100]))
    print()
    idx += 1
