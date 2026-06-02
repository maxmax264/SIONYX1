content = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

# הוסף buttonColor ל-DESIGN_DEFAULTS
old1 = '  showRegister: true,'
new1 = '  buttonColor: "",\n  showRegister: true,'
count1 = content.count(old1)
print(f'DEFAULTS match: {count1}')
if count1 == 1:
    content = content.replace(old1, new1, 1)

# הוסף ColorPicker לצבע כפתורים אחרי צבע משני
old2 = '        <Space align="center">\n          <Text style={{ width: 120 }}>׳©׳ ׳"׳׳¢׳¨׳›׳×:</Text>'
new2 = '        <Space align="center">\n          <Text style={{ width: 120 }}>צבע כפתורים:</Text>\n          <ColorPicker value={design.buttonColor || design.overlayColor1} onChange={(color) => handleDesignChange("buttonColor", color.toHexString())} />\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>׳©׳ ׳"׳׳¢׳¨׳›׳×:</Text>'
count2 = content.count(old2)
print(f'ColorPicker match: {count2}')
if count2 == 1:
    content = content.replace(old2, new2, 1)

if count1 == 1 and count2 == 1:
    open(r'.\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND - לא נשמר')
