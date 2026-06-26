import { useState, useEffect } from 'react';
import { Form, Switch, Input, Button, Alert } from 'antd';
import { App } from 'antd';
import { CreditCardOutlined } from '@ant-design/icons';
import { getPaymentSettings, updatePaymentSettings } from '../../services/paymentSettingsService';
import { useOrgId } from '../../hooks/useOrgId';

const PaymentSettings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveCardEnabled, setSaveCardEnabled] = useState(false);
  const { message } = App.useApp();
  const orgId = useOrgId();

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getPaymentSettings(orgId).then(res => {
      if (res.success) {
        form.setFieldsValue({ saveCardEnabled: res.payment.saveCardEnabled, nedarimApiValid: res.payment.nedarimApiValid || '' });
        setSaveCardEnabled(res.payment.saveCardEnabled);
      }
      setLoading(false);
    });
  }, [orgId, form]);

  const handleSave = async (values) => {
    if (!orgId) return;
    if (values.saveCardEnabled && !values.nedarimApiValid?.trim()) {
      message.error('נא להזין קוד API לשמירת כרטיס');
      return;
    }
    setSaving(true);
    const res = await updatePaymentSettings(orgId, { saveCardEnabled: values.saveCardEnabled, nedarimApiValid: values.nedarimApiValid || '' });
    if (res.success) { message.success('הגדרות תשלום נשמרו בהצלחה'); } else { message.error('שגיאה בשמירה: ' + res.error); }
    setSaving(false);
  };

  return (
    <div style={{ maxWidth: 520 }}>
      <p style={{ color: '#666', marginBottom: 20 }}>הגדרות שמירת כרטיס אשראי ללקוחות חוזרים. כאשר מופעל, הלקוח יוכל לסמן "שמור כרטיס" בדף התשלום ובפעם הבאה יצטרך להזין רק CVV.</p>
      <Form form={form} layout="vertical" onFinish={handleSave} initialValues={{ saveCardEnabled: false, nedarimApiValid: '' }}>
        <Form.Item name="saveCardEnabled" label="אפשר שמירת כרטיס אשראי" valuePropName="checked">
          <Switch disabled={loading} onChange={val => setSaveCardEnabled(val)} checkedChildren="פעיל" unCheckedChildren="כבוי" />
        </Form.Item>
        {saveCardEnabled && (
          <>
            <Alert type="info" showIcon style={{ marginBottom: 16 }} message="הכרטיס נשמר אצל נדרים פלוס בצורה מאובטחת (PCI DSS). המערכת שומרת רק טוקן." />
            <Form.Item name="nedarimApiValid" label="קוד API לשמירת כרטיסים (ApiValid מנדרים פלוס)" rules={[{ required: true, message: 'נא להזין קוד API' }]}>
              <Input placeholder="הזן את קוד ה-ApiValid מנדרים פלוס" disabled={loading} style={{ direction: 'ltr', fontFamily: 'monospace' }} />
            </Form.Item>
          </>
        )}
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={saving} icon={<CreditCardOutlined />}>שמור הגדרות</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default PaymentSettings;
