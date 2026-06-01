f=open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='import { Switch, Button, Input, Upload, Space, Typography, Divider, Image, Spin, App, Alert } from "antd";'
new='import { Switch, Button, Input, Upload, Space, Typography, Divider, Image, Spin, App, Alert, Tooltip } from "antd";\nimport { ReloadOutlined } from "@ant-design/icons";'
assert c.count(old)==1
c=c.replace(old,new,1)

old='  const handleDelete = async () => {'
new='''  const handleRefreshKiosk = async () => {
    setSaving(true);
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskRefreshAt`), Date.now().toString());
    message.success("הקיוסק יתרענן תוך 3 שניות");
    setSaving(false);
  };

  const handleDelete = async () => {'''
assert c.count(old)==1
c=c.replace(old,new,1)

old='      <Space align="center">\n        <Switch checked={enabled} onChange={handleToggle} loading={saving} />\n        <Text strong>הפעל תמונת רקע לקיוסק</Text>\n      </Space>'
new='''      <Space align="center" style={{ width: "100%", justifyContent: "space-between" }}>
        <Space align="center">
          <Switch checked={enabled} onChange={handleToggle} loading={saving} />
          <Text strong>הפעל תמונת רקע לקיוסק</Text>
        </Space>
        <Tooltip title="שולח פקודת רענון לקיוסק — התמונה תתעדכן תוך 3 שניות">
          <Button icon={<ReloadOutlined />} onClick={handleRefreshKiosk} loading={saving}>
            רענן קיוסק
          </Button>
        </Tooltip>
      </Space>'''
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\components\settings\KioskBackgroundSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
