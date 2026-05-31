f = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c = f.read()
f.close()

old = '    const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));\n    const orgSettingsSnap = await get(ref(database, "systemSettings/orgs"));\n    if (orgSettingsSnap.exists()) setOrgSettings(orgSettingsSnap.val() || {});'

new = '    try {\n      const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));\n      if (sysSnap.exists()) setMaxImageSizeMB(sysSnap.val());\n      const orgSettingsSnap = await get(ref(database, "systemSettings/orgs"));\n      if (orgSettingsSnap.exists()) setOrgSettings(orgSettingsSnap.val() || {});\n    } catch (e) {\n      console.warn("systemSettings read failed:", e.message);\n    }'

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
