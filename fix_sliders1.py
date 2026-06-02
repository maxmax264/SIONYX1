content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''        {design.cleanMode && (
          <Space direction="vertical" size={10} style={{ width: "100%", paddingRight: 8, borderRight: "3px solid #6366F1" }}>
            <Space align="center">
              <Text style={{ width: 120 }}>מיקום אופקי:</Text>
              <Slider min={5} max={95} value={design.formX ?? 50} onChange={val => setDesign({ ...design, formX: val })} onChangeComplete={val => handleDesignChange("formX", val)} style={{ width: 180 }} />
              <Text type="secondary" style={{ width: 30 }}>{design.formX ?? 50}%</Text>
            </Space>
            <Space align="center">
              <Text style={{ width: 120 }}>מיקום אנכי:</Text>
              <Slider min={10} max={90} value={design.formY ?? 50} onChange={val => setDesign({ ...design, formY: val })} onChangeComplete={val => handleDesignChange("formY", val)} style={{ width: 180 }} />
              <Text type="secondary" style={{ width: 30 }}>{design.formY ?? 50}%</Text>
            </Space>
            <Space align="center">
              <Text style={{ width: 120 }}>רוחב טופס:</Text>
              <Slider min={200} max={500} step={10} value={design.formWidth ?? 340} onChange={val => setDesign({ ...design, formWidth: val })} onChangeComplete={val => handleDesignChange("formWidth", val)} style={{ width: 180 }} />
              <Text type="secondary" style={{ width: 40 }}>{design.formWidth ?? 340}px</Text>
            </Space>
          </Space>
        )}'''

new = ''''''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
