import { useState, useEffect } from 'react';
import { Switch, Typography, Space, Alert, Spin } from 'antd';
import { PhoneOutlined } from '@ant-design/icons';
import { getPhoneVerificationSetting, setPhoneVerificationSetting } from '../../services/settingsService';
import { useOrgId } from '../../hooks/useOrgId';

const { Title, Text } = Typography;

const PhoneVerificationSettings = () => {
  const orgId = useOrgId();
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (!orgId) return;
    getPhoneVerificationSetting(orgId).then(res => {
      if (res.success) setEnabled(res.requirePhoneVerification);
      setLoading(false);
    });
  }, [orgId]);

  const handleChange = async (value) => {
    setSaving(true);
    setMessage(null);
    const res = await setPhoneVerificationSetting(orgId, value);
    if (res.success) {
      setEnabled(value);
      setMessage({ type: 'success', text: value ? 'אימות טלפון הופעל' : 'אימות טלפון בוטל' });
    } else {
      setMessage({ type: 'error', text: 'שגיאה בשמירה' });
    }
    setSaving(false);
  };

  if (loading) return <Spin />;

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={4} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
          <PhoneOutlined /> אימות טלפון
        </Title>
        <Text type="secondary">כאשר מופעל, משתמשים חייבים לאמת את הטלפון לפני כניסה ל-Kiosk</Text>
      </div>

      <Space align="center" size="middle">
        <Switch
          checked={enabled}
          onChange={handleChange}
          loading={saving}
          checkedChildren="פעיל"
          unCheckedChildren="כבוי"
        />
        <Text>{enabled ? 'חייב אימות טלפון לכניסה' : 'כניסה חופשית ללא אימות'}</Text>
      </Space>

      {message && (
        <Alert message={message.text} type={message.type} showIcon closable onClose={() => setMessage(null)} />
      )}

      <Alert
        type="info"
        showIcon
        message="איך זה עובד?"
        description="משתמש שלא אימת טלפון יראה מסך המתנה ב-Kiosk עם הוראות להתקשר. לאימות ידני — לחץ על כפתור 'אמת ידנית' בדף המשתמשים."
      />
    </Space>
  );
};

export default PhoneVerificationSettings;
