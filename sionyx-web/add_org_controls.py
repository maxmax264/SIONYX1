f = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c = f.read()
f.close()

old1 = '  const [savingSize, setSavingSize] = useState(false);'
new1 = '  const [savingSize, setSavingSize] = useState(false);\n  const [orgSettings, setOrgSettings] = useState({});\n  const [savingOrgSettings, setSavingOrgSettings] = useState({});'
assert c.count(old1) == 1
c = c.replace(old1, new1, 1)

old2 = '    const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));'
new2 = '    const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));\n    const orgSettingsSnap = await get(ref(database, "systemSettings/orgs"));\n    if (orgSettingsSnap.exists()) setOrgSettings(orgSettingsSnap.val() || {});'
assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

old3 = '  const handleSaveMaxSize = async () => {'
new3 = '  const handleSaveOrgSetting = async (orgId, field, value) => {\n    setSavingOrgSettings(prev => ({ ...prev, [orgId + field]: true }));\n    await set(ref(database, `systemSettings/orgs/${orgId}/${field}`), value);\n    setOrgSettings(prev => ({ ...prev, [orgId]: { ...(prev[orgId] || {}), [field]: value } }));\n    message.success("\u05d4\u05d2\u05d3\u05e8\u05d4 \u05e0\u05e9\u05de\u05e8\u05d4");\n    setSavingOrgSettings(prev => ({ ...prev, [orgId + field]: false }));\n  };\n  const handleSaveMaxSize = async () => {'
assert c.count(old3) == 1
c = c.replace(old3, new3, 1)

old4 = '    {\n      title: "\u05e4\u05d9\u05e7\u05d5\u05d7",'
new4 = '    {\n      title: "\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2",\n      key: "bgSettings",\n      render: (_, r) => {\n        const s = orgSettings[r.orgId] || {};\n        const allowUpload = s.allowFileUpload !== false;\n        const maxMB = s.maxImageSizeMB || 0;\n        return (\n          <Space direction="vertical" size={2}>\n            <Space size={4}>\n              <Switch size="small" checked={allowUpload} loading={!!savingOrgSettings[r.orgId + "allowFileUpload"]} onChange={v => handleSaveOrgSetting(r.orgId, "allowFileUpload", v)} />\n              <Text style={{ fontSize: 11 }}>\u05d4\u05e2\u05dc\u05d0\u05ea \u05e7\u05d5\u05d1\u05e5</Text>\n            </Space>\n            <Space size={4}>\n              <InputNumber size="small" min={0} value={maxMB} style={{ width: 60 }} onChange={v => setOrgSettings(prev => ({ ...prev, [r.orgId]: { ...(prev[r.orgId] || {}), maxImageSizeMB: v || 0 } }))} onBlur={() => handleSaveOrgSetting(r.orgId, "maxImageSizeMB", orgSettings[r.orgId]?.maxImageSizeMB || 0)} />\n              <Text style={{ fontSize: 11 }}>MB</Text>\n            </Space>\n          </Space>\n        );\n      },\n    },\n    {\n      title: "\u05e4\u05d9\u05e7\u05d5\u05d7",'
assert c.count(old4) == 1
c = c.replace(old4, new4, 1)

open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(c)
print("OK")
