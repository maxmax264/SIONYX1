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
        >'''

new = '''      <div
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
        >'''

count = content.count(old)
print(f"Found {count} matches - no change needed, adding brand panel")

old2 = '''        </div>
      </div>
    </div>
  );

  return ('''

new2 = '''        </div>
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
      </div>
    </div>
  );

  return ('''

count2 = content.count(old2)
print(f"Found2 {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
