import { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  Typography,
  Alert,
  Popconfirm,
  App,
} from 'antd';
import {
  CloudUploadOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { getLogShippingDestinations, saveLogShippingDestinations } from '../../services/logShippingService';
import { useOrgId } from '../../hooks/useOrgId';
import { logger } from '../../utils/logger';

const { Text } = Typography;

let tempIdCounter = 0;
const makeTempId = () => `new-${Date.now()}-${tempIdCounter++}`;

const LogShippingSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [rows, setRows] = useState([]);
  const { message } = App.useApp();
  const orgId = useOrgId();

  const load = async () => {
    setLoading(true);
    if (!orgId) { setLoading(false); return; }
    const result = await getLogShippingDestinations(orgId);
    if (result.success) {
      setRows(result.destinations);
    } else {
      message.error(result.error || 'שגיאה בטעינת אתרי הלוגים');
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [orgId]); // eslint-disable-line react-hooks/exhaustive-deps

  const updateRow = (id, field, value) => {
    setRows(prev => prev.map(r => (r.id === id ? { ...r, [field]: value } : r)));
  };

  const addRow = () => {
    setRows(prev => [
      ...prev,
      { id: makeTempId(), label: `אתר ${prev.length + 1}`, url: '', apiKey: '', intervalMs: 0, enabled: true },
    ]);
  };

  const removeRow = (id) => {
    setRows(prev => prev.filter(r => r.id !== id));
  };

  const handleSave = async () => {
    if (!orgId) { message.error('מזהה ארגון לא נמצא'); return; }
    setSaving(true);
    try {
      const result = await saveLogShippingDestinations(orgId, rows);
      if (result.success) {
        message.success('הגדרות שילוח הלוגים נשמרו בהצלחה');
        load(); // re-fetch so temp ids become the real saved keys
      } else {
        message.error(result.error || 'שגיאה בשמירת ההגדרות');
      }
    } catch (error) {
      logger.error('Save failed:', error);
      message.error('שגיאה בשמירת ההגדרות');
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    {
      title: 'שם האתר',
      dataIndex: 'label',
      render: (_, row) => (
        <Input
          value={row.label}
          onChange={e => updateRow(row.id, 'label', e.target.value)}
          placeholder='למשל: אתר ראשי'
          style={{ minWidth: 120 }}
        />
      ),
    },
    {
      title: 'כתובת URL',
      dataIndex: 'url',
      render: (_, row) => (
        <Input
          value={row.url}
          onChange={e => updateRow(row.id, 'url', e.target.value)}
          placeholder='https://example.onrender.com'
          style={{ minWidth: 220 }}
          dir='ltr'
        />
      ),
    },
    {
      title: 'API Key',
      dataIndex: 'apiKey',
      render: (_, row) => (
        <Input.Password
          value={row.apiKey}
          onChange={e => updateRow(row.id, 'apiKey', e.target.value)}
          placeholder='מפתח API של האתר'
          style={{ minWidth: 160 }}
          dir='ltr'
        />
      ),
    },
    {
      title: 'תדירות',
      dataIndex: 'intervalMs',
      render: (_, row) => (
        <InputNumber
          value={row.intervalMs}
          onChange={val => updateRow(row.id, 'intervalMs', val || 0)}
          min={0}
          step={500}
          addonAfter='מ״ש'
          style={{ width: 140 }}
        />
      ),
    },
    {
      title: 'פעיל',
      dataIndex: 'enabled',
      render: (_, row) => (
        <Switch checked={row.enabled} onChange={val => updateRow(row.id, 'enabled', val)} />
      ),
    },
    {
      title: '',
      render: (_, row) => (
        <Popconfirm title='להסיר את האתר?' onConfirm={() => removeRow(row.id)} okText='הסר' cancelText='ביטול'>
          <Button danger icon={<DeleteOutlined />} size='small' />
        </Popconfirm>
      ),
    },
  ];

  return (
    <Space direction='vertical' size='large' style={{ width: '100%' }}>
      <Alert
        message='שילוח לוגים מקיוסקים לאתרים חיצוניים'
        description='כל קיוסק שולח את הלוגים שלו בזמן אמת לאתר/ים המוגדרים כאן. ניתן להגדיר כמה אתרים במקביל, כל אחד עם תדירות שליחה ומפתח API נפרד. 0 מ"ש = שליחה מהירה ככל האפשר (בלי דיליי).'
        type='info'
        icon={<InfoCircleOutlined />}
        showIcon
      />
      <Card
        title='אתרי יעד ללוגים'
        extra={<CloudUploadOutlined />}
      >
        <Table
          dataSource={rows}
          columns={columns}
          rowKey='id'
          pagination={false}
          loading={loading}
          locale={{ emptyText: 'לא הוגדרו אתרים - הוסף אתר כדי להתחיל' }}
          scroll={{ x: true }}
        />
        <Space style={{ marginTop: 16 }}>
          <Button icon={<PlusOutlined />} onClick={addRow} disabled={loading}>
            הוסף אתר
          </Button>
          <Button type='primary' icon={<SaveOutlined />} onClick={handleSave} loading={saving} disabled={loading}>
            שמור הגדרות
          </Button>
        </Space>
      </Card>
      <Card title='מידע נוסף'>
        <Text type='secondary'>
          • השינויים חלים על כל הקיוסקים בארגון תוך כמה שניות, בלי צורך בהפעלה מחדש
          <br />
          • הסרת אתר מהרשימה עוצרת את השילוח אליו באופן מיידי
          <br />
          • אם לא הוגדר כאן אף אתר, הקיוסק ממשיך לשלוח לאתר ברירת המחדל (אם הוגדר ברג'יסטרי)
        </Text>
      </Card>
    </Space>
  );
};

export default LogShippingSettings;
