f=open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='''      <div style={{ background: "#f5f5f5", borderRadius: 12, padding: 16, marginBottom: 8 }}>
        <div style={{
          background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
          borderRadius: 10, padding: "24px 32px", color: "white", textAlign: "center"
        }}>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{design.brandName || "SIONYX"}</div>
          <div style={{ fontSize: 14, opacity: 0.85, marginTop: 6 }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
        </div>
        <div style={{ background: "white", borderRadius: 10, padding: "16px 24px", marginTop: 8 }}>
          <div style={{ fontWeight: 700, fontSize: 18 }}>{design.welcomeText || "ברוכים הבאים"}</div>
          <div style={{ color: "#888", fontSize: 13, marginTop: 4 }}>{design.welcomeSubtext || "התחבר לחשבון שלך"}</div>
          <div style={{ background: "#e8e8e8", borderRadius: 6, height: 36, marginTop: 12 }} />
          <div style={{ background: "#e8e8e8", borderRadius: 6, height: 36, marginTop: 8 }} />
          <div style={{ background: design.overlayColor1, borderRadius: 6, height: 36, marginTop: 12 }} />
          {design.showRegister && (
            <div style={{ textAlign: "center", marginTop: 8, color: "#888", fontSize: 12 }}>אין לך חשבון? הירשם</div>
          )}
        </div>
      </div>'''

new='''      <div style={{ background: "#e8e8e8", borderRadius: 12, padding: 12, marginBottom: 8 }}>
        <div style={{
          display: "flex", flexDirection: "row-reverse",
          borderRadius: 10, overflow: "hidden",
          boxShadow: "0 4px 24px rgba(99,102,241,0.2)",
          height: 280, background: "white"
        }}>
          {/* צד שמאל - פאנל צבעוני */}
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
          </div>
        </div>
      </div>'''

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\components\settings\AuthDesignSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
