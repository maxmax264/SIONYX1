content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
idx = content.find('getOrgMessages(selectedOrgId)')
print(content[idx-200:idx+300])
