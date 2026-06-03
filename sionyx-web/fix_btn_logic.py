f = open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()

old = 'background: (design.buttonColor && design.buttonColor !== "") ? design.buttonColor : design.overlayColor1, borderRadius: 6, height: 32'
new = 'background: design.buttonColor || design.overlayColor1, borderRadius: 6, height: 32'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
