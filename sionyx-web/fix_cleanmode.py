f=open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

# 1 - הוסף formPosition ל-DEFAULTS
old='  cleanMode: false,'
new='  cleanMode: false,\n  formPosition: "center",'
assert c.count(old)==1
c=c.replace(old,new,1)

# 2 - תקן תצוגה מקדימה במצב נקי
old='          {/* צד ימין - טופס */}\n          <div style={{ width: design.cleanMode ? "100%" : "50%", background: "rgba(255,255,255,0.95)", padding: 16, display: "flex", flexDirection: "column", justifyContent: "center", direction: "rtl" }}>'
new='''          {/* צד ימין - טופס */}
          <div style={{ width: design.cleanMode ? "100%" : "50%", background: design.cleanMode ? "transparent" : "rgba(255,255,255,0.95)", padding: 16, display: "flex", flexDirection: "column", justifyContent: "center", direction: "rtl",
            alignItems: design.cleanMode ? (design.formPosition === "right" ? "flex-end" : design.formPosition === "left" ? "flex-start" : "center") : "stretch" }}>
            {design.cleanMode && (
              <div style={{ width: 180, background: "rgba(255,255,255,0.93)", borderRadius: 8, padding: 12, boxShadow: "0 2px 12px rgba(0,0,0,0.15)" }}>'''
assert c.count(old)==1
c=c.replace(old,new,1)

# 3 - סגור את ה-div של הטופס במצב נקי
old='            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}\n          </div>'
new='''            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
            {design.cleanMode && </div>}
          </div>'''
assert c.count(old)==1
c=c.replace(old,new,1)

# 4 - הסר עריכת שם SIONYX
old='        <Space align="center">\n          <Text style={{ width: 110 }}>שם המערכת:</Text>\n          <Input value={design.brandName} onChange={e => setDesign({ ...design, brandName: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 180 }} />\n        </Space>'
new='        <Space align="center">\n          <Text style={{ width: 110 }}>שם המערכת:</Text>\n          <Text strong>{design.brandName}</Text>\n        </Space>'
assert c.count(old)==1
c=c.replace(old,new,1)

# 5 - הוסף בחירת מיקום טופס
old='        <Space align="center">\n          <Switch checked={design.cleanMode || false} onChange={val => handleDesignChange("cleanMode", val)} />\n          <Space direction="vertical" size={0}>\n            <Text>מצב נקי — טופס בלבד</Text>\n            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני, הלוגו יופיע מעל הטופס</Text>\n          </Space>\n        </Space>'
new='''        <Space align="center">
          <Switch checked={design.cleanMode || false} onChange={val => handleDesignChange("cleanMode", val)} />
          <Space direction="vertical" size={0}>
            <Text>מצב נקי — טופס בלבד</Text>
            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני</Text>
          </Space>
        </Space>
        {design.cleanMode && (
          <Space align="center">
            <Text style={{ width: 110 }}>מיקום טופס:</Text>
            {["right","center","left"].map(pos => (
              <Button key={pos} size="small" type={design.formPosition === pos ? "primary" : "default"}
                onClick={() => handleDesignChange("formPosition", pos)}>
                {pos === "right" ? "ימין" : pos === "center" ? "מרכז" : "שמאל"}
              </Button>
            ))}
          </Space>
        )}'''
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\components\settings\KioskDesignSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
