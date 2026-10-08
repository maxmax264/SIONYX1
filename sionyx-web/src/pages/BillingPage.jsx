import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert, Button, Card, Checkbox, Col, Form, Input, Modal, Row, Space, Spin, Statistic, Table, Tag, Typography, App,
} from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { useOrgId } from '../hooks/useOrgId';
import {
  getBillingSummary, getPayConfig, confirmBillingPayment, acceptContract,
} from '../services/billingService';

const { Text, Paragraph } = Typography;

const STATUS_TAG = {
  unpaid: { color: 'red', text: 'ממתין לתשלום' },
  claimed: { color: 'gold', text: 'שולם - ממתין לאימות' },
  paid: { color: 'green', text: 'שולם' },
  void: { color: 'default', text: 'בוטל' },
};

const NEDARIM_ORIGIN = 'https://matara.pro';
const NEDARIM_IFRAME = `${NEDARIM_ORIGIN}/nedarimplus/iframe?language=he&CVV=Hide`;

const fmtMonth = ym => dayjs(`${ym}-01`).format('MM/YYYY');
const money = n => `₪${(Math.round((n || 0) * 100) / 100).toLocaleString('he-IL')}`;

/** Card form (Nedarim's own iframe - card data never touches our servers). */
const PayModal = ({ open, invoice, orgId, onClose, onPaid }) => {
  const { message } = App.useApp();
  const [height, setHeight] = useState(260);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);
  const iframeRef = useRef(null);
  const monthRef = useRef(null);
  monthRef.current = invoice?.month;

  useEffect(() => {
    if (!open) return undefined;
    const handler = event => {
      // Only trust messages that really come from Nedarim's own iframe.
      if (event.origin !== NEDARIM_ORIGIN || !event.data || !event.data.Name) return;
      if (event.data.Name === 'Height') setHeight(parseInt(event.data.Value, 10) + 15);
      if (event.data.Name === 'TransactionResponse') {
        const r = event.data.Value || {};
        if (r.Status === 'OK') {
          confirmBillingPayment(orgId, monthRef.current, r.TransactionId)
            .catch(() => {})
            .finally(() => {
              setBusy(false);
              message.success('התשלום התקבל, תודה!');
              onPaid();
            });
        } else {
          setBusy(false);
          message.error(r.Message || 'התשלום נכשל');
        }
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [open, orgId, onPaid, message]);

  const pay = async () => {
    if (!name.trim()) return message.warning('נא להזין שם מלא');
    setBusy(true);
    try {
      const cfg = await getPayConfig(orgId, invoice.month);
      iframeRef.current?.contentWindow?.postMessage({
        Name: 'FinishTransaction2',
        Value: {
          Mosad: cfg.mosadId, ApiValid: cfg.apiValid, PaymentType: 'Ragil', Currency: '1', Zeout: '',
          FirstName: name.trim(), LastName: '', Street: '', City: '', Phone: phone.trim(), Mail: email.trim(),
          Amount: String(cfg.amount), Tashlumim: '1', Groupe: '', Comment: cfg.comment,
          Param1: cfg.month, Param2: orgId, ForceUpdateMatching: '0',
          CallBack: cfg.callbackUrl, CallBackMailError: '',
        },
      }, NEDARIM_ORIGIN);
    } catch (e) {
      setBusy(false);
      message.error(e.message);
    }
  };

  const left = invoice ? (invoice.amount || 0) - (invoice.paidAmount || 0) : 0;
  return (
    <Modal open={open} onCancel={busy ? undefined : onClose} footer={null} destroyOnClose width={520}
      title={invoice ? `תשלום עבור ${fmtMonth(invoice.month)} - ${money(left)}` : 'תשלום'}>
      <Space direction='vertical' style={{ width: '100%' }} size={10}>
        <Input placeholder='שם מלא' value={name} onChange={e => setName(e.target.value)} />
        <Input placeholder='טלפון' dir='ltr' value={phone} onChange={e => setPhone(e.target.value)} />
        <Input placeholder='אימייל (לקבלה)' dir='ltr' value={email} onChange={e => setEmail(e.target.value)} />
        <iframe ref={iframeRef} title='nedarim' src={NEDARIM_IFRAME}
          style={{ width: '100%', border: 'none', height }} />
        <Button type='primary' size='large' block loading={busy} onClick={pay}>
          {`שלם ${money(left)}`}
        </Button>
      </Space>
    </Modal>
  );
};

const ContractCard = ({ orgId, summary, onAccepted }) => {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [busy, setBusy] = useState(false);
  const submit = async values => {
    setBusy(true);
    try {
      await acceptContract(orgId, { ...values, agree: true });
      message.success('ההסכם נחתם');
      onAccepted();
    } catch (e) {
      message.error(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Card size='small' title='הסכם שימוש - נדרשת חתימה' style={{ marginBottom: 16 }}>
      <div style={{
        whiteSpace: 'pre-wrap', maxHeight: 220, overflowY: 'auto', padding: 12,
        border: '1px solid #e5e7eb', borderRadius: 8, marginBottom: 12, background: '#fafafa',
      }}>
        {summary.config.contractText}
      </div>
      <Form form={form} layout='vertical' onFinish={submit}>
        <Row gutter={12}>
          <Col xs={24} md={8}>
            <Form.Item name='fullName' label='שם מלא' rules={[{ required: true, message: 'נא למלא שם' }]}>
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name='idNumber' label='ת.ז.'><Input dir='ltr' /></Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name='role' label='תפקיד'><Input /></Form.Item>
          </Col>
        </Row>
        <Form.Item name='agree' valuePropName='checked'
          rules={[{ validator: (_, v) => (v ? Promise.resolve() : Promise.reject(new Error('יש לאשר את ההסכם'))) }]}>
          <Checkbox>קראתי והסכמתי לתנאי ההסכם, ושמי המוקלד לעיל מהווה חתימתי</Checkbox>
        </Form.Item>
        <Button type='primary' htmlType='submit' loading={busy}>חתימה על ההסכם</Button>
      </Form>
    </Card>
  );
};

const BillingPage = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [payInvoice, setPayInvoice] = useState(null);

  const load = useCallback(async () => {
    if (!orgId) return;
    setLoading(true);
    try {
      setSummary(await getBillingSummary(orgId));
    } catch (e) {
      message.error(e.message);
    } finally {
      setLoading(false);
    }
  }, [orgId, message]);

  useEffect(() => { load(); }, [load]);

  if (!summary) return <div style={{ textAlign: 'center', padding: 60 }}><Spin /></div>;
  if (summary.exempt) return <Empty404 />;

  const open = summary.invoices.filter(i => i.status === 'unpaid' || i.status === 'claimed');
  const due = open.reduce((s, i) => s + (i.amount - (i.paidAmount || 0)), 0);
  const paid = summary.invoices.reduce((s, i) => s + (i.paidAmount || 0), 0);
  const est = summary.estimate;
  const needContract = summary.contract.required && !summary.contract.accepted;

  const columns = [
    { title: 'חודש', dataIndex: 'month', render: fmtMonth },
    { title: 'סכום', dataIndex: 'amount', render: money },
    { title: 'שולם', dataIndex: 'paidAmount', render: money },
    { title: 'מועד אחרון לתשלום', dataIndex: 'dueAt', render: v => dayjs(v).format('DD/MM/YYYY') },
    { title: 'סטטוס', dataIndex: 'status', render: s => <Tag color={STATUS_TAG[s]?.color}>{STATUS_TAG[s]?.text || s}</Tag> },
    {
      title: 'פירוט', key: 'bd',
      render: (_, r) => r.breakdown
        ? `${r.breakdown.full} מלא · ${r.breakdown.half} חצי · ${r.breakdown.none} ללא חיוב${r.breakdown.minimumApplied ? ' · חל מינימום' : ''}`
        : '',
    },
    {
      title: '', key: 'pay',
      render: (_, r) => (r.status === 'unpaid' ? (
        <Button type='primary' size='small' onClick={() => setPayInvoice(r)}>שלם</Button>
      ) : null),
    },
  ];

  return (
    <Space direction='vertical' style={{ width: '100%' }} size={16}>
      {summary.status?.state === 'warning' && (
        <Alert type='warning' showIcon message='קיימת יתרה לתשלום' />
      )}
      {needContract && <ContractCard orgId={orgId} summary={summary} onAccepted={load} />}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}><Card size='small'><Statistic title='יתרה לתשלום' value={money(due)} valueStyle={{ color: due > 0 ? '#cf1322' : undefined }} /></Card></Col>
        <Col xs={24} md={8}><Card size='small'><Statistic title='שולם עד כה' value={money(paid)} /></Card></Col>
        <Col xs={24} md={8}><Card size='small'><Statistic title={`החודש (${fmtMonth(est.month)}) - הערכה`} value={money(est.total)} /></Card></Col>
      </Row>
      <Card size='small' title='איך מחושב החיוב'>
        <Paragraph style={{ marginBottom: 4 }}>
          {`מחשב שפעל ב-${summary.config.fullMonthThresholdPct}% מימי החודש ומעלה: ${money(est.pricePerComputer)}. `}
          {`מחשב שפעל לפחות יום אחד: ${money(est.pricePerComputer / 2)}. מחשב שלא פעל: ללא חיוב. `}
          {`מינימום חיוב חודשי: ${money(est.minimumMonthly)}.`}
        </Paragraph>
        <Text type='secondary'>
          {`החודש עד כה: ${est.full} מחשבים במחיר מלא, ${est.half} בחצי מחיר, ${est.none} ללא חיוב`}
          {est.minimumApplied ? ' (חל מינימום חיוב)' : ''}
        </Text>
      </Card>
      <Card size='small' title='חשבוניות' extra={<Button icon={<ReloadOutlined />} onClick={load} loading={loading} />}>
        <Table rowKey='month' columns={columns} dataSource={summary.invoices} pagination={false} size='small'
          scroll={{ x: 'max-content' }} locale={{ emptyText: 'עדיין לא הופקו חשבוניות' }} />
      </Card>
      {summary.contract.accepted && (
        <Text type='secondary'>
          {`ההסכם נחתם על ידי ${summary.contract.acceptedBy} בתאריך ${dayjs(summary.contract.acceptedAt).format('DD/MM/YYYY')}`}
        </Text>
      )}
      <PayModal open={!!payInvoice} invoice={payInvoice} orgId={orgId}
        onClose={() => setPayInvoice(null)} onPaid={() => { setPayInvoice(null); load(); }} />
    </Space>
  );
};

const Empty404 = () => (
  <Card><Text type='secondary'>אין חיובים לארגון זה.</Text></Card>
);

export default BillingPage;
