f = open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
print(repr(c[1000:1200]))
