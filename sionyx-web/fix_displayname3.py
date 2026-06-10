import re

content = open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8').read()

# 1. Add MessageOutlined to imports
content = content.replace(
    "import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined, LockOutlined } from '@ant-design/icons';",
    "import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined, LockOutlined, MessageOutlined } from '@ant-design/icons';"
)

# 2. Add useState hooks and service imports after existing imports
content = content.replace(
    "import KioskPasswordSettings from '../components/settings/KioskPasswordSettings';",
    """import KioskPasswordSettings from '../components/settings/KioskPasswordSettings';
import { App, Input, Button, Form } from 'antd';
import { getDisplayName, updateDisplayName } from '../services/settingsService';
import { useOrgId } from '../hooks/useOrgId';"""
)

# 3. Add DisplayNameSettings component before SettingsPage
old_comp = "const SettingsPage = () => {"
new_comp = """const DisplayNameSettings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const { message } = App.useApp();
  const orgId = useOrgId();

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getDisplayName(orgId).then(res => {
      if (res.success) form.setFieldsValue({ displayName: res.displayName });
      setLoading(false);
    });
  }, [orgId, form]);

  const handleSave = async (values) => {
    if (!orgId) return;
    setSaving(true);
    const res = await updateDisplayName(orgId, values.displayName || '');
    if (res.success) {
      message.success('השם נשמר בהצלחה');
    } else {
      message.error('שגיאה בשמירה');
    }
    setSaving(false);
  };

  return (
    <div style={{ maxWidth: 480 }}>
      <p style={{ color: '#666', marginBottom: 16 }}>
        השם שיוצג ללקוחות בקיוסק כאשר הם מקבלים הודעה ממך.
        לדוגמה: "מקס כושר" יוצג כ"שלח הודעה למקס כושר".
      </p>
      <Form form={form} layout="vertical" onFinish={handleSave}>
        <Form.Item
          label="שם החנות לתצוגה בהודעות"
          name="displayName"
          rules={[{ required: true, message: 'נא להזין שם' }]}
        >
          <Input
            placeholder='לדוגמה: מקס כושר'
            maxLength={40}
            disabled={loading}
            style={{ direction: 'rtl' }}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={saving}>
            שמור
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const SettingsPage = () => {"""

content = content.replace(old_comp, new_comp)

# 4. Add messages tab to tabs array
content = content.replace(
    "    {\n      key: 'downloads',",
    """    {
      key: 'messages',
      label: (
        <span>
          <MessageOutlined />
          {' '}הודעות
        </span>
      ),
      children: <DisplayNameSettings />,
    },
    {
      key: 'downloads',"""
)

open(r'.\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
print('OK')
