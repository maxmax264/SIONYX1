content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', encoding='utf-8').read()

old = """    const messages = Object.entries(data).map(([id, msg]) => ({ id, ...msg }));"""

new = """    const messages = Object.entries(data)
      .filter(([, msg]) => msg.fromSupervisor === true)
      .map(([id, msg]) => ({ id, ...msg }));"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\services\supervisorMessageService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
