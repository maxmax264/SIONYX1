import { useState, useEffect } from 'react';
import { Form, Switch, Input, Button, Alert, Divider } from 'antd';
import { App } from 'antd';
import { CreditCardOutlined, BankOutlined, SafetyOutlined } from '@ant-design/icons';
import { getPaymentSettings, updatePaymentSettings, getBillingSettings, updateBillingSettings } from '../../services/paymentSettingsService';
import { useOrgId } from '../../hooks/useOrgId';

const PaymentSettings = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveCardEnabled, setSaveCardEnabled] = useState(false);
  const [billingConfigured, setBillingConfigured] = useState(false);
  const { message } = App.useApp();
  const orgId = useOrgId();

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    Promise.all([getPaymentSettings(orgId), getBillingSettings(orgId)]).then(([paymentRes, billingRes]) => {
      if (paymentRes.success) {
        form.setFieldsValue({
          saveCardEnabled: paymentRes.payment.saveCardEnabled,
          nedarimApiValid: paymentRes.payment.nedarimApiValid || '',
        });
        setSaveCardEnabled(paymentRes.payment.saveCardEnabled);
      }
      if (billingRes.success) {
        form.setFieldsValue({
          billingNedarimMosadId: billingRes.billing.nedarimMosadId || '',
          billingNedarimApiValid: billingRes.billing.nedarimApiValid || '',
        });
        setBillingConfigured(billingRes.billing.billingConfigured);
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
    const [paymentRes, billingRes] = await Promise.all([
      updatePaymentSettings(orgId, { saveCardEnabled: values.saveCardEnabled, nedarimApiValid: values.nedarimApiValid || '' }),
      updateBillingSettings(orgId, {
        nedarimMosadId: values.billingNedarimMosadId || '',
        nedarimApiValid: values.billingNedarimApiValid || '',
      }),
    ]);
    if (paymentRes.success && billingRes.success) {
      message.success('הגדרות תשלום נשמרו בהצלחה');
      setBillingConfigured(billingRes.billingConfigured);
    } else {
      message.error('שגיאה בשמירה: ' + (paymentRes.error || billingRes.error));
    }
    setSaving(false);
  };

  return (
    <div style={{ maxWidth: 520 }}>
      {!billingConfigured && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 20 }}
          message="חיוב לא מוגדר"
          description="לא הוזנו פרטי חיוב של נדרים פלוס. יש להזין אותם כדי שהלקוחות יוכלו לבצע רכישות."
        />
      )}

      <h4 style={{ margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
        <BankOutlined /> פרטי חיוב נדרים פלוס
      </h4>
      <p style={{ color: '#666', marginBottom: 20 }}>הזן את מזהה המוסד ומפתח ה-API של נדרים פלוס כדי לאפשר תשלומים בארגון.</p>
      <Form form={form} layout="vertical" onFinish={handleSave} initialValues={{ saveCardEnabled: false, nedarimApiValid: '', billingNedarimMosadId: '', billingNedarimApiValid: '' }}>
        <Form.Item name="billingNedarimMosadId" label="מזהה מוסד NEDARIM">
          <Input placeholder="הזן את מזהה המוסד" disabled={loading} style={{ direction: 'ltr', fontFamily: 'monospace' }} prefix={<BankOutlined />} />
        </Form.Item>
        <Form.Item name="billingNedarimApiValid" label="מפתח API של NEDARIM">
          <Input placeholder="הזן את מפתח ה-API" disabled={loading} style={{ direction: 'ltr', fontFamily: 'monospace' }} prefix={<SafetyOutlined />} />
        </Form.Item>

        <Divider style={{ margin: '24px 0' }} />

        <h4 style={{ margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
          <CreditCardOutlined /> שמירת כרטיס אשראי
        </h4>
        <p style={{ color: '#666', marginBottom: 20 }}>הגדרות שמירת כרטיס אשראי ללקוחות חוזרים. כאשר מופעל, הלקוח יוכל לסמן "שמור כרטיס" בדף התשלום ובפעם הבאה יצטרך להזין רק CVV.</p>
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
