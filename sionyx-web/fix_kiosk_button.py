f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
old = 'background: design.overlayColor1, borderRadius: 5, height: 26, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600 }}>כניסה לחשבון</div>'
new = 'background: design.buttonColor || design.overlayColor1, borderRadius: 5, height: 26, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600 }}>כניסה לחשבון</div>'
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
