import { useEffect, useState } from 'react';
import {
  Card,
  Form,
  InputNumber,
  Button,
  Space,
  Typography,
  Alert,
  Switch,
  App,
} from 'antd';
import {
  ClockCircleOutlined,
  SaveOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { getIdleTimeoutSetting, updateIdleTimeoutSetting } from '../../services/settingsService';
import { useOrgId } from '../../hooks/useOrgId';
import { logger } from '../../utils/logger';

const { Text } = Typography;

const IdleTimeoutSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const orgId = useOrgId();

  const loadSetting = async () => {
    setLoading(true);
    if (!orgId) { setLoading(false); return; }
    const result = await getIdleTimeoutSetting(orgId);
    if (result.success) {
      setEnabled(result.enabled);
      form.setFieldsValue({ minutes: result.minutes || 5 });
    } else {
      message.error(result.error || 'שגיאה בטעינת ההגדרה');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadSetting();
  }, [orgId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (!orgId) { message.error('מזהה ארגון לא נמצא'); return; }
      setSaving(true);
      const result = await updateIdleTimeoutSetting(orgId, enabled, values.minutes);
      if (result.success) {
        message.success('הגדרת הניתוק האוטומטי עודכנה בהצלחה');
      } else {
        message.error(result.error || 'שגיאה בשמירת ההגדרה');
      }
    } catch (error) {
      logger.error('Validation failed:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Space direction='vertical' size='large' style={{ width: '100%' }}>
      <Alert
        message='ניתוק אוטומטי בעקבות חוסר פעילות'
        description='כשלקוח לא מגיב במחשב (עכבר/מקלדת) פרק זמן מוגדר, הקיוסק ינתק אותו אוטומטית כדי לפנות את התור. ניתן לכבות את הניתוק האוטומטי לחלוטין.'
        type='info'
        icon={<InfoCircleOutlined />}
        showIcon
      />
      <Card title='הגדרת ניתוק אוטומטי' extra={<ClockCircleOutlined />}>
        <Form form={form} layout='vertical' onFinish={handleSave}>
          <Form.Item label='ניתוק אוטומטי בעקבות חוסר פעילות'>
            <Switch
              checked={enabled}
              onChange={setEnabled}
              disabled={loading}
              checkedChildren='מופעל'
              unCheckedChildren='כבוי (לעולם לא)'
            />
          </Form.Item>
          <Form.Item
            name='minutes'
            label='ניתוק אחרי (דקות) של חוסר פעילות'
            rules={enabled ? [
              { required: true, message: 'נא להזין מספר דקות' },
              { type: 'number', min: 1, max: 120, message: 'בין 1 ל-120 דקות' },
            ] : []}
          >
            <InputNumber
              min={1}
              max={120}
              style={{ width: 200 }}
              disabled={loading || !enabled}
              addonAfter='דקות'
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type='primary'
              htmlType='submit'
              icon={<SaveOutlined />}
              loading={saving}
              disabled={loading}
            >
              שמור הגדרה
            </Button>
          </Form.Item>
        </Form>
      </Card>
      <Card title='מידע נוסף'>
        <Text type='secondary'>
          • ההגדרה חלה על כל מחשבי הקיוסק בארגון, ומסונכרנת אוטומטית עם ההתחלה הבאה של סשן
          <br />
          • כברירת מחדל: ניתוק אחרי 5 דקות (כמו שהיה קודם)
          <br />
          • כשההגדרה כבויה, סשן לא ינותק בגלל חוסר פעילות (רק בסיום זמן/יציאה ידנית)
        </Text>
      </Card>
    </Space>
  );
};

export default IdleTimeoutSettings;
