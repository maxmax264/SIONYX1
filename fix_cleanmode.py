content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''      <div
        style={{
          width: 800,
          height: 560,
          background: "white",
          borderRadius: 20,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,.25)",
          position: "relative",
          display: "flex",
          zIndex: 1,
        }}
      >
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
        {!design.cleanMode && (
          <div
            style={{
              width: 320,
              background: `linear-gradient(160deg, ${design.overlayColor1}, ${design.overlayColor2})`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              color: "white",
              padding: 40,
            }}
          >
            <div style={{ fontSize: 42, fontWeight: 800 }}>SIONYX</div>
            <div style={{ marginTop: 14, opacity: 0.9, textAlign: "center" }}>{design.brandSubtitle}</div>
          </div>
        )}
      </div>'''

new = '''      {design.cleanMode ? (
        <FormBox />
      ) : (
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
            zIndex: 1,
          }}
        >
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
          <div
            style={{
              width: 320,
              background: `linear-gradient(160deg, ${design.overlayColor1}, ${design.overlayColor2})`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              color: "white",
              padding: 40,
            }}
          >
            <div style={{ fontSize: 42, fontWeight: 800 }}>SIONYX</div>
            <div style={{ marginTop: 14, opacity: 0.9, textAlign: "center" }}>{design.brandSubtitle}</div>
          </div>
        </div>
      )}'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
