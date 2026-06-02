f=open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='''            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
            {design.cleanMode && </div>}
          </div>'''
new='''            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
          </div>
          )}
        </div>'''
count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\KioskDesignSettings.jsx','w',encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
