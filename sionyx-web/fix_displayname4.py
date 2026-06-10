content = open(r'.\src\supervisor\pages\SupervisorSettingsPage.jsx', encoding='utf-8').read()

new_content = """import { useState, useEffect } from 'react';
import { Card, Descriptions, Typography, Form, Input, Button, App, Divider } from 'antd';
import { UserOutlined, PhoneOutlined, SettingOutlined, MessageOutlined } from '@ant-design/icons';
import { useSupervisorAuthStore } from '../store/supervisorAuthStore';
import { getSupervisorDisplayName, updateSupervisorDisplayName } from '../services/supervisorMessageService';
import { getAuth } from 'firebase/auth';

const { Title } = Typography;

const SupervisorSettingsPage = () => {
  const supervisor = useSupervisorAuthStore(state => state.supervisor);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const { message } = App.useApp();

  const orgCount = supervisor?.orgIds?.length || 0;

  useEffect(() => {
    const auth = getAuth();
    const uid = auth.currentUser?.uid;
    if (!uid) return;
    setLoading(true);
    getSupervisorDisplayName(uid).then(res => {
      if (res.success) form.setFieldsValue({ displayName: res.displayName });
      setLoading(false);
    });
  }, [form]);

  const handleSave = async (values) => {
    const auth = getAuth();
    const uid = auth.currentUser?.uid;
    if (!uid) return;
    setSaving(true);
    const res = await updateSupervisorDisplayName(uid, values.displayName || '');
    if (res.success) {
      message.success('השם נשמר בהצלחה');
    } else {
      message.error('שגיאה בשמירה');
    }
    setSaving(false);
  };

  return (
    <div style={{ direction: 'rtl', maxWidth: 600, margin: '0 auto' }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <SettingOutlined style={{ marginLeft: 8 }} />
        הגדרות
      </Title>

      <Card size='small' title='פרופיל מפקח' styles={{ body: { padding: 0 } }}>
        <Descriptions column={1} bordered size='small'>
          <Descriptions.Item label={<><UserOutlined style={{ marginLeft: 8 }} />שם</>}>
            {supervisor?.name || '-'}
          </Descriptions.Item>
          <Descriptions.Item label={<><PhoneOutlined style={{ marginLeft: 8 }} />טלפון</>}>
            {supervisor?.phone || '-'}
          </Descriptions.Item>
          <Descriptions.Item label='ארגונים בפיקוח'>
            {orgCount}
          </Descriptions.Item>
          <Descriptions.Item label='תאריך יצירה'>
            {supervisor?.createdAt
              ? new Date(supervisor.createdAt).toLocaleDateString('he-IL')
              : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card
        size='small'
        title={<><MessageOutlined style={{ marginLeft: 8 }} />שם לתצוגה בהודעות</>}
        style={{ marginTop: 16 }}
      >
        <p style={{ color: '#666', marginBottom: 16 }}>
          השם שיוצג ללקוחות בקיוסק כאשר הם מקבלים הודעה ממך.
          לדוגמה: "חותם" יוצג כ"שלח הודעה לפיקוח חותם".
        </p>
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            label="שם הפיקוח לתצוגה"
            name="displayName"
            rules={[{ required: true, message: 'נא להזין שם' }]}
          >
            <Input
              placeholder='לדוגמה: חותם'
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
      </Card>
    </div>
  );
};

export default SupervisorSettingsPage;
"""

open(r'.\src\supervisor\pages\SupervisorSettingsPage.jsx', 'w', encoding='utf-8').write(new_content)
print('OK')
