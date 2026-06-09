import { useEffect, useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  Typography,
  Alert,
  App,
} from 'antd';
import {
  LockOutlined,
  SaveOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { getKioskExitPassword, updateKioskExitPassword } from '../../services/settingsService';
import { useOrgId } from '../../hooks/useOrgId';
import { logger } from '../../utils/logger';

const { Text } = Typography;

const KioskPasswordSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const orgId = useOrgId();

  const loadPassword = async () => {
    setLoading(true);
    if (!orgId) { setLoading(false); return; }
    const result = await getKioskExitPassword(orgId);
    if (result.success) {
      form.setFieldsValue({ password: result.password, confirm: result.password });
    } else {
      message.error(result.error || 'שגיאה בטעינת הסיסמה');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadPassword();
  }, [orgId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (!orgId) { message.error('מזהה ארגון לא נמצא'); return; }
      setSaving(true);
      const result = await updateKioskExitPassword(orgId, values.password);
      if (result.success) {
        message.success('סיסמת היציאה עודכנה בהצלחה');
      } else {
        message.error(result.error || 'שגיאה בשמירת הסיסמה');
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
        message='סיסמת יציאה מהקיוסק'
        description='הסיסמה משמשת לצאת ממצב קיוסק ולגשת למערכת ההפעלה. שמור על הסיסמה בסוד.'
        type='warning'
        icon={<InfoCircleOutlined />}
        showIcon
      />
      <Card title='שינוי סיסמת יציאה' extra={<LockOutlined />}>
        <Form form={form} layout='vertical' onFinish={handleSave}>
          <Form.Item
            name='password'
            label='סיסמה חדשה'
            rules={[
              { required: true, message: 'נא להזין סיסמה' },
              { min: 4, message: 'הסיסמה חייבת להכיל לפחות 4 תווים' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder='הזן סיסמה חדשה'
              iconRender={visible => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
              style={{ maxWidth: 400 }}
              disabled={loading}
            />
          </Form.Item>
          <Form.Item
            name='confirm'
            label='אימות סיסמה'
            dependencies={['password']}
            rules={[
              { required: true, message: 'נא לאמת את הסיסמה' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('הסיסמאות אינן תואמות'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder='הזן שוב את הסיסמה'
              iconRender={visible => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
              style={{ maxWidth: 400 }}
              disabled={loading}
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
              שמור סיסמה
            </Button>
          </Form.Item>
        </Form>
      </Card>
      <Card title='מידע נוסף'>
        <Text type='secondary'>
          • הסיסמה נשמרת ב-שרת ומסונכרנת לקיוסק אוטומטית
          <br />
          • הסיסמה הנוכחית תישאר בתוקף עד שהקיוסק יסנכרן
          <br />
          • מינימום 4 תווים
        </Text>
      </Card>
      <Card title='סיסמא ללא אינטרנט (מקומית)' extra={<LockOutlined />}>
        <Alert
          message='שים לב — כשאין אינטרנט הסיסמא משתנה אוטומטית!'
          description='כאשר המחשב אינו מחובר לאינטרנט, הקיוסק לא יכול לאמת מול השרת ולכן עובר אוטומטית לסיסמא המקומית. כלומר — אם אין אינטרנט, הסיסמא שהגדרת למעלה לא תעבוד, ובמקומה תצטרך להשתמש בסיסמא המקומית.'
          type='warning'
          showIcon
          style={{ marginBottom: 16 }}
        />
        <Text strong>כדי לשנות את הסיסמא המקומית:</Text>
        <ol style={{ marginTop: 8, paddingRight: 20 }}>
          <li>פתח את תוכנת הקיוסק על המחשב הרצוי</li>
          <li>הכנס את קוד היציאה (Ctrl+Alt+Space)</li>
          <li>לחץ קליק ימני על האייקון בשורת המשימות</li>
          <li>בחר <strong>הגדרות</strong></li>
          <li>שנה את הסיסמא המקומית</li>
        </ol>
        <Alert
          message='סיסמת ברירת מחדל לאחר התקנה: 1234 — מומלץ לשנות אותה!'
          type='warning'
          showIcon
          style={{ marginTop: 12 }}
        />
      </Card>
    </Space>
  );
};

export default KioskPasswordSettings;
