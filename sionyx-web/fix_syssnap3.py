f = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c = f.read()
f.close()

old = '    }\n    if (sysSnap.exists()) setMaxImageSizeMB(sysSnap.val());\n    if (orgsRes.success)'
new = '    }\n    if (orgsRes.success)'

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
