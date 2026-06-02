f=open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='  const Preview = () => (\n    <div style={{ borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(99,102,241,0.2)", height: 260, position: "relative" }}>\n      {enabled && imageUrl && (\n        <img src={imageUrl} alt="bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.55 }} />\n      )}\n      <div style={{ position: "relative", zIndex: 1, display: "flex", height: "100%", background: enabled && imageUrl ? "transparent" : "#f0f0f0" }}>\n        {!design.cleanMode && (\n          <div style={{ width: "50%", height: "100%", background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "white", padding: 16 }}>\n            <div style={{ fontSize: 18, fontWeight: 800 }}>{design.brandName || "SIONYX"}</div>\n            <div style={{ fontSize: 11, opacity: 0.85, marginTop: 6, textAlign: "center" }}>{design.brandSubtitle}</div>\n          </div>\n        )}\n        <div style={{ width: design.cleanMode ? "100%" : "50%", background: "rgba(255,255,255,0.92)", padding: 16, display: "flex", flexDirection: "column", justifyContent: "center", direction: "rtl" }}>\n          {design.cleanMode && <div style={{ textAlign: "center", marginBottom: 12, fontWeight: 800, fontSize: 18, color: design.overlayColor1 }}>{design.brandName}</div>}\n          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{design.welcomeText}</div>\n          <div style={{ color: "#888", fontSize: 11, marginBottom: 12 }}>{design.welcomeSubtext}</div>\n          <div style={{ background: "#f0f0f0", borderRadius: 4, height: 24, marginBottom: 6 }} />\n          <div style={{ background: "#f0f0f0", borderRadius: 4, height: 24, marginBottom: 10 }} />\n          <div style={{ background: design.overlayColor1, borderRadius: 4, height: 28, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11 }}>כניסה לחשבון</div>\n          {design.showRegister && <div style={{ textAlign: "center", marginTop: 6, color: "#888", fontSize: 10 }}>אין לך חשבון? הירשם</div>}\n        </div>\n      </div>\n    </div>\n  );'

new='''  const Preview = () => (
    <div style={{ borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(99,102,241,0.2)", height: 260, position: "relative", background: "#333" }}>
      {enabled && imageUrl && (
        <img src={imageUrl} alt="bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.55 }} />
      )}
      <div style={{ position: "absolute", inset: 0, zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "flex", flexDirection: "row", width: "80%", height: "80%", borderRadius: 10, overflow: "hidden", boxShadow: "0 2px 16px rgba(0,0,0,0.3)" }}>
          {/* צד ימין - טופס */}
          <div style={{ width: design.cleanMode ? "100%" : "50%", background: "rgba(255,255,255,0.95)", padding: 16, display: "flex", flexDirection: "column", justifyContent: "center", direction: "rtl" }}>
            {design.cleanMode && <div style={{ textAlign: "center", marginBottom: 8, fontWeight: 800, fontSize: 14, color: design.overlayColor1 }}>{design.brandName}</div>}
            <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 2 }}>{design.welcomeText}</div>
            <div style={{ color: "#888", fontSize: 9, marginBottom: 8 }}>{design.welcomeSubtext}</div>
            <div style={{ background: "#f0f0f0", borderRadius: 4, height: 18, marginBottom: 4 }} />
            <div style={{ background: "#f0f0f0", borderRadius: 4, height: 18, marginBottom: 8 }} />
            <div style={{ background: design.overlayColor1, borderRadius: 4, height: 22, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9 }}>כניסה לחשבון</div>
            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
          </div>
          {/* צד שמאל - פאנל צבעוני */}
          {!design.cleanMode && (
            <div style={{ width: "50%", height: "100%", background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "white", padding: 12 }}>
              <div style={{ fontSize: 14, fontWeight: 800 }}>{design.brandName || "SIONYX"}</div>
              <div style={{ fontSize: 9, opacity: 0.85, marginTop: 4, textAlign: "center" }}>{design.brandSubtitle}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );'''

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\components\settings\KioskDesignSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
