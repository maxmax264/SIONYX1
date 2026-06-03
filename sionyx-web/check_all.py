f = open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
idx = c.find('buttonColor')
while idx != -1:
    print(f"pos {idx}: {repr(c[idx:idx+40])}")
    idx = c.find('buttonColor', idx+1)
