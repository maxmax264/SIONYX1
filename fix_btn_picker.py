content = open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8').read()

old = '          <Text type="secondary">{design.overlayColor2}</Text>\n        </Space>\n      </Space>\n\n      <Divider>'
new = '          <Text type="secondary">{design.overlayColor2}</Text>\n        </Space>\n        <Space align="center">\n          <Text style={{ width: 120 }}>צבע כפתורים:</Text>\n          <ColorPicker value={design.buttonColor || design.overlayColor1}\n            onChange={(color) => handleChange("buttonColor", color.toHexString())} />\n          <Text type="secondary">{design.buttonColor || design.overlayColor1}</Text>\n        </Space>\n      </Space>\n\n      <Divider>'

if old in content:
    content = content.replace(old, new, 1)
    print("Added buttonColor picker: OK")
else:
    print("NOT FOUND")

open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(content)
