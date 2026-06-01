f=open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='  const [maxSizeMB, setMaxSizeMB] = useState(null);'
new='  const [maxSizeMB, setMaxSizeMB] = useState(null);\n  const [allowFileUpload, setAllowFileUpload] = useState(false);'
assert c.count(old)==1
c=c.replace(old,new,1)

old='      const sysSnap = await get(dbRef(database, "systemSettings/maxImageSizeMB"));\n      if (sysSnap.exists()) setMaxSizeMB(sysSnap.val());'
new='      const sysSnap = await get(dbRef(database, "systemSettings/maxImageSizeMB"));\n      if (sysSnap.exists()) setMaxSizeMB(sysSnap.val());\n      const uploadSnap = await get(dbRef(database, `organizations/${orgId}/metadata/allowFileUpload`));\n      setAllowFileUpload(uploadSnap.exists() && uploadSnap.val() === true);'
assert c.count(old)==1
c=c.replace(old,new,1)

old='          <Divider>העלאת קובץ</Divider>\n          <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">\n            <Button icon={<UploadOutlined />} loading={saving}>בחר תמונה</Button>\n          </Upload>\n          {maxSizeMB && <Text type="secondary">גודל מקסימלי: {maxSizeMB}MB</Text>}\n\n          <Divider>או הדבק קישור</Divider>'
new='          {allowFileUpload && (\n            <>\n              <Divider>העלאת קובץ</Divider>\n              <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">\n                <Button icon={<UploadOutlined />} loading={saving}>בחר תמונה</Button>\n              </Upload>\n              {maxSizeMB && <Text type="secondary">גודל מקסימלי: {maxSizeMB}MB</Text>}\n            </>\n          )}\n\n          <Divider>הדבק קישור</Divider>'
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\components\settings\KioskBackgroundSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
