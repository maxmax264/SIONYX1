content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()
idx = content.find('getOrgUserReplies')
print(repr(content[idx:idx+400]))
