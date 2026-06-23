content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\SystemServicesManager.cs', encoding='utf-8').read()

# בדוק מה יש בפועל
idx = content.find('isKiosk')
print(repr(content[idx:idx+150]))
