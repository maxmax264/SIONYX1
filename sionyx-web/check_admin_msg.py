content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', encoding='utf-8').read()
idx = content.find('getOrgMessages')
print(content[idx:idx+400])
