f=open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='      const uploadSnap = await get(dbRef(database, `organizations/${orgId}/metadata/allowFileUpload`));\n      setAllowFileUpload(uploadSnap.exists() && uploadSnap.val() === true);'
new='      const uploadSnap = await get(dbRef(database, `systemSettings/orgs/${orgId}/allowFileUpload`));\n      setAllowFileUpload(!uploadSnap.exists() || uploadSnap.val() !== false);'

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\components\settings\KioskBackgroundSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
