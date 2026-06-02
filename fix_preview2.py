content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''      {enabled && imageUrl && (
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
        >'''

new = '''      {enabled && imageUrl && (
        <img
          src={imageUrl}
          alt=""
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            zIndex: 0,
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
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
