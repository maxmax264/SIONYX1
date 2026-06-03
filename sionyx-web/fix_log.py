f = open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()

old = 'onChange={(color) => handleChange("buttonColor", color.toHexString())}'
new = 'onChange={(color) => { console.log("NEW COLOR:", color.toHexString()); handleChange("buttonColor", color.toHexString()); }}'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
