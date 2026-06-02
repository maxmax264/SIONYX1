content = open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8').read()

# הוסף buttonColor ל-DEFAULTS
old = '  overlayColor2: "#8B5CF6",'
new = '  overlayColor2: "#8B5CF6",\n  buttonColor: "#6366F1",'
content = content.replace(old, new, 1)

# עדכן את כפתור התצוגה המקדימה לשימוש ב-buttonColor
old2 = 'background: design.overlayColor1, borderRadius: 6, height: 32'
new2 = 'background: design.buttonColor || design.overlayColor1, borderRadius: 6, height: 32'
content = content.replace(old2, new2, 1)

# הוסף ColorPicker לכפתורים אחרי overlayColor2
old3 = '        <Space align="center">\n          <Text style={{ width: 120 }}>׳¦׳\'׳¢ ׳׳©׳ ׳™:</Text>\n          <ColorPicker value={design.overlayColor2}\n            onChange={(color) => handleChange("overlayColor2", color.toHexString())} />\n          <Text type="secondary">{design.overlayColor2}</Text>\n        </Space>\n      </Space>'
new3 = '        <Space align="center">\n          <Text style={{ width: 120 }}>׳¦׳\'׳¢ ׳׳©׳ ׳™:</Text>\n          <ColorPicker value={design.overlayColor2}\n            onChange={(color) => handleChange("overlayColor2", color.toHexString())} />\n          <Text type="secondary">{design.overlayColor2}</Text>\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>׳¦׳\'׳¢ ׳›׳₪׳×׳•׳¨׳™׳:</Text>\n          <ColorPicker value={design.buttonColor || design.overlayColor1}\n            onChange={(color) => handleChange("buttonColor", color.toHexString())} />\n          <Text type="secondary">{design.buttonColor || design.overlayColor1}</Text>\n        </Space>\n      </Space>'

if old3 in content:
    content = content.replace(old3, new3, 1)
    print("Added buttonColor picker: OK")
else:
    print("ColorPicker section NOT FOUND - adding manually")

print(f"DEFAULTS updated: {'buttonColor' in content}")
open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(content)
