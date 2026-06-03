f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
old = '''            <div
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
              \u05d4\u05ea\u05d7\u05d1\u05e8\u05d5\u05ea'''
new = '''            <div
              style={{
                height: 48,
                background: design.buttonColor || design.overlayColor1,
                borderRadius: 8,
                color: "white",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                fontWeight: 700,
              }}
            >
              \u05d4\u05ea\u05d7\u05d1\u05e8\u05d5\u05ea'''
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
