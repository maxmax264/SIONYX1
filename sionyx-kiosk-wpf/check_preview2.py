f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
idx = c.find('formX ?? 50')
if idx == -1:
    idx = c.find('formX}')
print(c[idx-100:idx+300])
