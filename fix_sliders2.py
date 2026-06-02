content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''      {design.cleanMode ? (
        <FormBox />
      ) : ('''

new = '''      {design.cleanMode ? (
        <>
          <FormBox />
          <div style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            background: "rgba(0,0,0,0.6)",
            padding: "12px 20px",
            zIndex: 10,
            display: "flex",
            gap: 24,
            alignItems: "center",
            direction: "rtl",
          }}>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>אופקי: {design.formX ?? 50}%</Text>
              <Slider min={5} max={95} value={design.formX ?? 50}
                onChange={val => setDesign({ ...design, formX: val })}
                onChangeComplete={val => handleDesignChange("formX", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>אנכי: {design.formY ?? 50}%</Text>
              <Slider min={10} max={90} value={design.formY ?? 50}
                onChange={val => setDesign({ ...design, formY: val })}
                onChangeComplete={val => handleDesignChange("formY", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>רוחב: {design.formWidth ?? 340}px</Text>
              <Slider min={200} max={500} step={10} value={design.formWidth ?? 340}
                onChange={val => setDesign({ ...design, formWidth: val })}
                onChangeComplete={val => handleDesignChange("formWidth", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
          </div>
        </>
      ) : ('''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
