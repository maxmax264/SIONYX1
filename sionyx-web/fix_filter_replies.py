content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()

old = "      .filter(([, r]) => r.fromSupervisorReply === true)"
new = "      .filter(([, r]) => r.fromSupervisorReply === true && !r.deleted)"

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
