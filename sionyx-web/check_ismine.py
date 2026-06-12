content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
idx = content.find('const isMine')
print(content[idx-50:idx+200])
