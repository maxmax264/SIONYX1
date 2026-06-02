f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
fields = ['overlayColor1', 'overlayColor2', 'buttonColor', 'brandSubtitle', 
          'welcomeText', 'welcomeSubtext', 'showRegister', 'cleanMode']
print('=== שדות שנשמרים ל-Firebase ===')
for field in fields:
    count = c.count(field)
    status = 'OK' if count > 0 else 'MISSING'
    print(f'{status} ({count}x): {field}')
