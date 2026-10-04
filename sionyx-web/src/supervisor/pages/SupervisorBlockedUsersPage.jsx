import { useEffect, useRef, useState } from 'react';
import { Card, Row, Col, Button, Spin, App, Typography, Empty, Tag, Modal, Input, Alert, theme } from 'antd';
import { CheckCircleOutlined, StopOutlined, PhoneOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import { getBlockedUsers, unblockUser, blockUsersBulk, parseBlockList } from '../services/supervisorBlockService';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const SupervisorBlockedUsersPage = () => {
  const [loading, setLoading] = useState(true);
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [unblockingPhone, setUnblockingPhone] = useState(null);
  const { message } = App.useApp();
  const { token } = theme.useToken();
  const fileRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [importReason, setImportReason] = useState('');
  const [importing, setImporting] = useState(false);

  const handleFile = async e => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    const parsed = parseBlockList(await file.text());
    if (parsed.valid.length === 0 && parsed.invalid.length === 0) {
      message.error('לא נמצאו מספרי טלפון בקובץ');
      return;
    }
    const existing = new Set(blockedUsers.map(b => b.phone));
    setPreview({
      ...parsed,
      fresh: parsed.valid.filter(v => !existing.has(v.phone)),
      already: parsed.valid.filter(v => existing.has(v.phone)).length,
    });
  };

  const handleImport = async () => {
    setImporting(true);
    const res = await blockUsersBulk(preview.fresh, importReason || 'חסימה מרשימה');
    if (res.success) {
      message.success(`נחסמו ${res.total} מספרים (${res.flaggedUsers} משתמשים קיימים)`);
      setPreview(null);
      setImportReason('');
      loadData();
    } else {
      message.error(res.error || 'שגיאה בייבוא');
    }
    setImporting(false);
  };

  const handleExport = () => {
    const rows = blockedUsers.map(b => [b.phone, b.userName || b.name || '', b.reason || ''].join(','));
    const blob = new Blob(['\uFEFF' + rows.join('\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'blocked-numbers.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const loadData = async () => {
    setLoading(true);
    const result = await getBlockedUsers();
    if (result.success) {
      setBlockedUsers(result.blockedUsers || []);
    } else {
      message.error(result.error || 'שגיאה בטעינת המשתמשים החסומים');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUnblock = async phone => {
    setUnblockingPhone(phone);
    const result = await unblockUser(phone);
    if (result?.success !== false) {
      message.success('המשתמש שוחרר מחסימה');
      loadData();
    } else {
      message.error(result?.error || 'שגיאה בשחרור חסימה');
    }
    setUnblockingPhone(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
        <Spin size='large' />
      </div>
    );
  }

  return (
    <div style={{ direction: 'rtl', maxWidth: 960, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>
          <StopOutlined style={{ marginLeft: 8 }} />
          משתמשים חסומים
        </Title>
        <div style={{ display: 'flex', gap: 8 }}>
          <input ref={fileRef} type='file' accept='.csv,.txt' style={{ display: 'none' }} onChange={handleFile} />
          <Button type='primary' icon={<UploadOutlined />} onClick={() => fileRef.current?.click()}>
            העלאת רשימת חסומים
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport} disabled={blockedUsers.length === 0}>
            ייצוא
          </Button>
        </div>
      </div>

      <Modal
        title='אישור חסימת מספרים'
        open={!!preview}
        onOk={handleImport}
        onCancel={() => setPreview(null)}
        okText={`חסום ${preview?.fresh.length || 0} מספרים`}
        cancelText='ביטול'
        confirmLoading={importing}
        okButtonProps={{ disabled: !preview?.fresh.length }}
      >
        {preview && (
          <div style={{ direction: 'rtl', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Alert
              type='info'
              showIcon
              message={`${preview.fresh.length} חדשים · ${preview.already} כבר חסומים · ${preview.invalid.length} לא תקינים`}
            />
            {preview.invalid.length > 0 && (
              <Text type='secondary' style={{ fontSize: 12 }}>
                לא תקינים (לא ייחסמו): {preview.invalid.slice(0, 10).join(', ')}
                {preview.invalid.length > 10 ? ' ...' : ''}
              </Text>
            )}
            <Input placeholder='סיבת חסימה (אופציונלי)' value={importReason} onChange={e => setImportReason(e.target.value)} />
          </div>
        )}
      </Modal>

      {blockedUsers.length === 0 ? (
        <Card size='small'>
          <Empty description='אין משתמשים חסומים' />
        </Card>
      ) : (
        <Row gutter={[12, 12]}>
          {blockedUsers.map(user => (
            <Col xs={24} sm={12} key={user.phone}>
              <Card size='small' styles={{ body: { padding: 16 } }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <Text strong>{user.userName || user.name || user.phone}</Text>
                  <Tag color='error'>חסום</Tag>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <PhoneOutlined style={{ fontSize: 12, color: token.colorTextTertiary }} />
                    <Text type='secondary' style={{ fontSize: 13 }}>{user.phone}</Text>
                  </div>
                  {user.reason && (
                    <Text type='secondary' style={{ fontSize: 12 }}>
                      סיבה: {user.reason}
                    </Text>
                  )}
                  {user.blockedAt && (
                    <Text type='secondary' style={{ fontSize: 12 }}>
                      {dayjs(user.blockedAt).format('DD/MM/YYYY HH:mm')}
                    </Text>
                  )}
                </div>

                <Button
                  type='primary'
                  size='small'
                  block
                  icon={<CheckCircleOutlined />}
                  loading={unblockingPhone === user.phone}
                  onClick={() => handleUnblock(user.phone)}
                >
                  שחרר חסימה
                </Button>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default SupervisorBlockedUsersPage;
