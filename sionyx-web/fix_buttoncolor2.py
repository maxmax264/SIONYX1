f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()

old = 'toHexString())} />\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>שם המערכת:</Text>'
new = 'toHexString())} />\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>צבע כפתורים:</Text>\n          <ColorPicker value={design.buttonColor || design.overlayColor1} onChange={(color) => handleDesignChange("buttonColor", color.toHexString())} />\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>שם המערכת:</Text>'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
