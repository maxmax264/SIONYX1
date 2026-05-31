f=open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c=f.read()
f.close()

# Add InputNumber to imports
old1 = 'import { Card, Row, Col, Typography, Statistic, Table, Tag, Button, Switch, Space, Spin, App, theme, Modal, Form, Input } from "antd";'
new1 = 'import { Card, Row, Col, Typography, Statistic, Table, Tag, Button, Switch, Space, Spin, App, theme, Modal, Form, Input, InputNumber } from "antd";'
c = c.replace(old1, new1, 1)

# Add PictureOutlined to icon imports
old2 = 'import { BankOutlined, UserOutlined, TeamOutlined, EyeOutlined, EyeInvisibleOutlined, LaptopOutlined, ReloadOutlined, KeyOutlined } from "@ant-design/icons";'
new2 = 'import { BankOutlined, UserOutlined, TeamOutlined, EyeOutlined, EyeInvisibleOutlined, LaptopOutlined, ReloadOutlined, KeyOutlined, PictureOutlined } from "@ant-design/icons";'
c = c.replace(old2, new2, 1)

# Add firebase database import
old3 = 'import { getAllOrgs, getAllSupervisors, connectToSupervision, disconnectFromSupervision } from "../services/ownerOrgService";'
new3 = 'import { getAllOrgs, getAllSupervisors, connectToSupervision, disconnectFromSupervision } from "../services/ownerOrgService";\nimport { ref, get, set } from "firebase/database";\nimport { database } from "../../config/firebase";'
c = c.replace(old3, new3, 1)

# Add state and load logic
old4 = '  const [passwordLoading, setPasswordLoading] = useState(false);'
new4 = '  const [passwordLoading, setPasswordLoading] = useState(false);\n  const [maxImageSizeMB, setMaxImageSizeMB] = useState(0);\n  const [savingSize, setSavingSize] = useState(false);'
c = c.replace(old4, new4, 1)

# Add load of systemSettings
old5 = '    const [orgsRes, supRes] = await Promise.all([getAllOrgs(), getAllSupervisors()]);'
new5 = '    const [orgsRes, supRes] = await Promise.all([getAllOrgs(), getAllSupervisors()]);\n    const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));\n    if (sysSnap.exists()) setMaxImageSizeMB(sysSnap.val());'
c = c.replace(old5, new5, 1)

# Add save handler before handleLogout
old6 = '  const handleLogout = async () => {'
new6 = '''  const handleSaveMaxSize = async () => {
    setSavingSize(true);
    await set(ref(database, "systemSettings/maxImageSizeMB"), maxImageSizeMB || 0);
    message.success("\u05d4\u05d2\u05d3\u05e8\u05d4 \u05e0\u05e9\u05de\u05e8\u05d4");
    setSavingSize(false);
  };
  const handleLogout = async () => {'''
c = c.replace(old6, new6, 1)

# Add card after organizations table card
old7 = '      <Modal title="\u05e9\u05d9\u05e0\u05d5\u05d9 \u05e1\u05d9\u05e1\u05de\u05d0\u05d4"'
new7 = '''      <Card title={<span><PictureOutlined /> \u05d4\u05d2\u05d3\u05e8\u05d5\u05ea \u05de\u05e2\u05e8\u05db\u05ea</span>} size="small" style={{ marginTop: 16 }}>
        <Space align="center">
          <Text>\u05d2\u05d5\u05d3\u05dc \u05de\u05e7\u05e1\u05d9\u05de\u05dc\u05d9 \u05dc\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 (MB) \u2014 0 = \u05dc\u05dc\u05d0 \u05d4\u05d2\u05d1\u05dc\u05d4:</Text>
          <InputNumber min={0} value={maxImageSizeMB} onChange={v => setMaxImageSizeMB(v || 0)} style={{ width: 100 }} />
          <Button type="primary" onClick={handleSaveMaxSize} loading={savingSize}>\u05e9\u05de\u05d5\u05e8</Button>
        </Space>
      </Card>
      <Modal title="\u05e9\u05d9\u05e0\u05d5\u05d9 \u05e1\u05d9\u05e1\u05de\u05d0\u05d4"'''
c = c.replace(old7, new7, 1)

open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(c)
print("OK")
