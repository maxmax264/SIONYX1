content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''  const Preview = () => (
    <div style={{ position: "relative", width: "100%", height: PREV_H, borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(99,102,241,0.18)", background: "#1a1a2e" }}>
      {/* רקע */}
      {enabled && imageUrl
        ? <img src={imageUrl} alt="bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />
        : <div style={{ position: "absolute", inset: 0, background: `linear-gradient(135deg, ${design.overlayColor1}33, ${design.overlayColor2}33)` }} />
      }
      {/* פאנל צבעוני — רק במצב רגיל */}
      {!design.cleanMode && (
        <div style={{ position: "absolute", right: 0, top: 0, width: "42%", height: "100%", background: `linear-gradient(160deg, ${design.overlayColor1}, ${design.overlayColor2})`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "white", padding: 16 }}>
          <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: 1 }}>{design.brandName}</div>
          <div style={{ fontSize: 11, opacity: 0.85, marginTop: 6, textAlign: "center" }}>{design.brandSubtitle}</div>
        </div>
      )}
      {/* טופס */}
      {design.cleanMode
        ? <FormBox />
        : (
          <div style={{ position: "absolute", left: 0, top: 0, width: "58%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ width: "80%", background: "rgba(255,255,255,0.96)", borderRadius: 10, padding: "16px 20px", direction: "rtl" }}>
              <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 2 }}>{design.welcomeText}</div>
              <div style={{ color: "#888", fontSize: 9, marginBottom: 8 }}>{design.welcomeSubtext}</div>
              <div style={{ background: "#f0f0f0", borderRadius: 4, height: 16, marginBottom: 5 }} />
              <div style={{ background: "#f0f0f0", borderRadius: 4, height: 16, marginBottom: 8 }} />
              <div style={{ background: design.overlayColor1, borderRadius: 4, height: 22, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10 }}>כניסה לחשבון</div>
              {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
            </div>
          </div>
        )
      }
      <div style={{ position: "absolute", bottom: 6, left: 8, fontSize: 9, color: "rgba(255,255,255,0.5)" }}>תצוגה מקדימה</div>
    </div>
  );'''

new = '''  const Preview = () => (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: 500,
        background: "#f5f5f5",
        borderRadius: 16,
        overflow: "hidden",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: 20,
      }}
    >
      {enabled && imageUrl && (
        <img
          src={imageUrl}
          alt=""
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      )}
      <div
        style={{
          width: 800,
          height: 560,
          background: "white",
          borderRadius: 20,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,.25)",
          position: "relative",
          display: "flex",
        }}
      >
        <div
          style={{
            width: 400,
            background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
            display: design.cleanMode ? "none" : "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            color: "white",
            padding: 40,
          }}
        >
          <div style={{ fontSize: 42, fontWeight: 800 }}>SIONYX</div>
          <div style={{ marginTop: 14, opacity: .9, textAlign: "center" }}>{design.brandSubtitle}</div>
        </div>
        <div
          style={{
            flex: 1,
            padding: 50,
            direction: "rtl",
            background: "white",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <h2>{design.welcomeText}</h2>
          <div style={{ color: "#888", marginBottom: 30 }}>{design.welcomeSubtext}</div>
          <div style={{ height: 46, background: "#f1f1f1", borderRadius: 8, marginBottom: 14 }} />
          <div style={{ height: 46, background: "#f1f1f1", borderRadius: 8, marginBottom: 20 }} />
          <div
            style={{
              height: 48,
              background: design.overlayColor1,
              borderRadius: 8,
              color: "white",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              fontWeight: 700,
            }}
          >
            התחברות
          </div>
          {design.showRegister && (
            <div style={{ textAlign: "center", marginTop: 15, color: "#888" }}>אין חשבון? הירשם</div>
          )}
        </div>
      </div>
    </div>
  );'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
