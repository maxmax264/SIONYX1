content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
idx = content.find('userMessages.filter')
if idx == -1:
    idx = content.find('userMessages.map')
print(content[idx-100:idx+200])
