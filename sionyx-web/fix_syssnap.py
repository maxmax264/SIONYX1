f = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c = f.read()
f.close()

idx = c.find('sysSnap')
print(repr(c[idx-50:idx+200]))
