f=open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='  showRegister: true,'
new='  showRegister: true,\n  cleanMode: false,'
assert c.count(old)==1
c=c.replace(old,new,1)

old='''      <Divider>אפשרויות</Divider>
      <Space align="center">
        <Switch checked={design.showRegister}
          onChange={val => handleChange("showRegister", val)} />
        <Text>הצג כפתור הרשמה</Text>
      </Space>'''
new='''      <Divider>אפשרויות</Divider>
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Switch checked={design.showRegister}
            onChange={val => handleChange("showRegister", val)} />
          <Text>הצג כפתור הרשמה</Text>
        </Space>
        <Space align="center">
          <Switch checked={design.cleanMode || false}
            onChange={val => handleChange("cleanMode", val)} />
          <Space direction="vertical" size={0}>
            <Text>מצב נקי — טופס בלבד</Text>
            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני, הלוגו יופיע מעל הטופס</Text>
          </Space>
        </Space>
      </Space>'''
assert c.count(old)==1
c=c.replace(old,new,1)

old='''        {/* צד שמאל - פאנל צבעוני */}
          <div style={{
            width: "50%", height: "100%",
            background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
            display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
            color: "white", padding: "24px"
          }}>
            <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: 2 }}>{design.brandName || "SIONYX"}</div>
            <div style={{ fontSize: 12, opacity: 0.85, marginTop: 8, textAlign: "center" }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
          </div>
          {/* צד ימין - טופס התחברות */}
          <div style={{
            width: "50%", height: "100%",
            background: "white", padding: "24px",
            display: "flex", flexDirection: "column", justifyContent: "center",
            direction: "rtl"
          }}>
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{design.welcomeText || "ברוכים הבאים"}</div>
            <div style={{ color: "#888", fontSize: 11, marginBottom: 16 }}>{design.welcomeSubtext || "התחבר לחשבון שלך"}</div>
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 8 }} />
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 12 }} />
            <div style={{ background: design.overlayColor1, borderRadius: 6, height: 32, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12 }}>כניסה לחשבון</div>
            {design.showRegister && (
              <div style={{ textAlign: "center", marginTop: 8, color: "#888", fontSize: 11 }}>אין לך חשבון? הירשם</div>
            )}
          </div>'''
new='''        {!design.cleanMode && (
            <div style={{
              width: "50%", height: "100%",
              background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              color: "white", padding: "24px"
            }}>
              <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: 2 }}>{design.brandName || "SIONYX"}</div>
              <div style={{ fontSize: 12, opacity: 0.85, marginTop: 8, textAlign: "center" }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
            </div>
          )}
          <div style={{
            width: design.cleanMode ? "100%" : "50%", height: "100%",
            background: "white", padding: "24px",
            display: "flex", flexDirection: "column", justifyContent: "center",
            direction: "rtl"
          }}>
            {design.cleanMode && (
              <div style={{ textAlign: "center", marginBottom: 16 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: design.overlayColor1 }}>{design.brandName || "SIONYX"}</div>
                <div style={{ fontSize: 11, color: "#888", marginTop: 4 }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
              </div>
            )}
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{design.welcomeText || "ברוכים הבאים"}</div>
            <div style={{ color: "#888", fontSize: 11, marginBottom: 16 }}>{design.welcomeSubtext || "התחבר לחשבון שלך"}</div>
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 8 }} />
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 12 }} />
            <div style={{ background: design.overlayColor1, borderRadius: 6, height: 32, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12 }}>כניסה לחשבון</div>
            {design.showRegister && (
              <div style={{ textAlign: "center", marginTop: 8, color: "#888", fontSize: 11 }}>אין לך חשבון? הירשם</div>
            )}
          </div>'''
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\components\settings\AuthDesignSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
