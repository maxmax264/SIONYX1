content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()
idx = content.find('fromSupervisor')
print(content[idx-200:idx+200])
