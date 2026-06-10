import { useState, useEffect } from 'react';
import { Card, Typography, Tabs, Space } from 'antd';
import { SettingOutlined, DollarOutlined, DownloadOutlined, PhoneOutlined, LockOutlined, MessageOutlined } from '@ant-design/icons';
import PricingSettings from '../components/settings/PricingSettings';
import PhoneVerificationSettings from '../components/settings/PhoneVerificationSettings';
import KioskDesignSettings from '../components/settings/KioskDesignSettings';
import DownloadsSettings from '../components/settings/DownloadsSettings';
import KioskPasswordSettings from '../components/settings/KioskPasswordSettings';
import { App, Input, Button, Form } from 'antd';
import { getDisplayName, updateDisplayName } from '../services/settingsService';
import { useOrgId } from '../hooks/useOrgId';

const { Title, Text } = Typography;

const useIsMobile = (breakpoint = 768) => {
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < breakpoint);
  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);
    const handler = (e) => setIsMobile(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [breakpoint]);
  return isMobile;
};

const DisplayNameSettings = () => {
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

const SettingsPage = () => {
  const isMobile = useIsMobile();
  const tabs = [
    {
      key: 'pricing',
      label: (
        <span>
          <DollarOutlined />
          {' '}תמחור הדפסות
        </span>
      ),
      children: <PricingSettings />,
    },
    {
      key: 'kioskdesign',
      label: (
        <span>
          <DownloadOutlined />
          {' '}עיצוב מסך קיוסק
        </span>
      ),
      children: <KioskDesignSettings />,
    },
    {
      key: 'phone',
      label: (
        <span>
          <PhoneOutlined />
          {' '}אימות טלפון
        </span>
      ),
      children: <PhoneVerificationSettings />,
    },
    {
      key: 'password',
      label: (
        <span>
          <LockOutlined />
          {' '}סיסמת יציאה
        </span>
      ),
      children: <KioskPasswordSettings />,
    },
    {
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
      key: 'downloads',
      label: (
        <span>
          <DownloadOutlined />
          {' '}הורדות
        </span>
      ),
      children: <DownloadsSettings />,
    },
  ];
  return (
    <div style={{ direction: 'rtl' }}>
      <Space direction='vertical' size='large' style={{ width: '100%' }}>
        <div
          className='page-header'
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 12,
            padding: isMobile ? '0 4px' : undefined,
          }}
        >
          <div>
            <Title
              level={isMobile ? 3 : 2}
              style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}
            >
              <SettingOutlined />
              הגדרות
            </Title>
            <Text type='secondary' style={{ fontSize: isMobile ? 12 : 14 }}>
              ניהול הגדרות הארגון שלך
            </Text>
          </div>
        </div>
        <Card styles={{ body: { padding: isMobile ? '12px 8px' : undefined } }}>
          <Tabs
            defaultActiveKey='pricing'
            items={tabs}
            tabPosition={isMobile ? 'top' : 'right'}
            style={{ minHeight: isMobile ? undefined : 400 }}
          />
        </Card>
      </Space>
    </div>
  );
};

export default SettingsPage;
