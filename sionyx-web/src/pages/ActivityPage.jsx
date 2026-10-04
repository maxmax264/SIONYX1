import { useEffect, useMemo, useState, useCallback } from 'react';
import { Card, Table, Tag, Input, Segmented, Row, Col, Typography, Button, Space, Empty } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import StatCard from '../components/StatCard';
import { getAllUsers } from '../services/userService';
import { useOrgId } from '../hooks/useOrgId';
import { logger } from '../utils/logger';

const { Text } = Typography;

const DAY = 24 * 60 * 60 * 1000;

/** Parse ISO string / ms number into ms, or null. */
const toMs = v => {
  if (v === undefined || v === null || v === '') return null;
  const ms = typeof v === 'number' ? v : new Date(v).getTime();
  return Number.isNaN(ms) ? null : ms;
};

/** Last entry: explicit lastLoginAt, else an active session start, else chat lastSeen. */
const getLastLoginMs = u => toMs(u.lastLoginAt) ?? toMs(u.sessionStartTime) ?? toMs(u.lastSeen);

const startOfToday = () => dayjs().startOf('day').valueOf();

const relativeLabel = ms => {
  if (!ms) return 'לא נכנס';
  const days = Math.floor((startOfToday() - dayjs(ms).startOf('day').valueOf()) / DAY);
  if (days <= 0) return 'היום';
  if (days === 1) return 'אתמול';
  return `לפני ${days} ימים`;
};

const statusOf = ms => {
  if (!ms) return { label: 'לא נכנס מעולם', color: 'default' };
  const age = Date.now() - ms;
  if (age <= 7 * DAY) return { label: 'פעיל', color: 'success' };
  if (age <= 30 * DAY) return { label: 'פחות פעיל', color: 'warning' };
  return { label: 'לא פעיל', color: 'error' };
};

const formatTime = secs => {
  const s = Math.max(0, Math.floor(secs || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return h > 0 ? `${h}:${String(m).padStart(2, '0')} שע׳` : `${m} דק׳`;
};

const FILTERS = [
  { label: 'הכל', value: 'all' },
  { label: 'היום', value: 'today' },
  { label: 'אתמול', value: 'yesterday' },
  { label: '7 ימים', value: '7' },
  { label: '30 ימים', value: '30' },
  { label: 'לא פעילים', value: 'inactive' },
];

const ActivityPage = () => {
  const orgId = useOrgId();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const load = useCallback(async () => {
    if (!orgId) return;
    setLoading(true);
    const res = await getAllUsers(orgId);
    if (!res.success) logger.error('Failed to load activity data:', res.error);
    setUsers(res.users || []);
    setLoading(false);
  }, [orgId]);

  useEffect(() => {
    load();
  }, [load]);

  const rows = useMemo(
    () =>
      users.map(u => ({
        key: u.uid,
        name: `${u.firstName || ''} ${u.lastName || ''}`.trim() || 'ללא שם',
        phone: u.phoneNumber || '',
        email: u.email || '',
        lastLogin: getLastLoginMs(u),
        createdAt: toMs(u.createdAt),
        remainingTime: u.remainingTime || 0,
        loginCount: u.loginCount || 0,
        inSession: !!u.isSessionActive,
      })),
    [users]
  );

  const stats = useMemo(() => {
    const today = startOfToday();
    return {
      today: rows.filter(r => r.lastLogin && r.lastLogin >= today).length,
      week: rows.filter(r => r.lastLogin && Date.now() - r.lastLogin <= 7 * DAY).length,
      inactive: rows.filter(r => !r.lastLogin || Date.now() - r.lastLogin > 30 * DAY).length,
      total: rows.length,
    };
  }, [rows]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const today = startOfToday();
    return rows.filter(r => {
      if (q && !`${r.name} ${r.phone} ${r.email}`.toLowerCase().includes(q)) return false;
      const t = r.lastLogin;
      switch (filter) {
        case 'today':
          return !!t && t >= today;
        case 'yesterday':
          return !!t && t >= today - DAY && t < today;
        case '7':
          return !!t && Date.now() - t <= 7 * DAY;
        case '30':
          return !!t && Date.now() - t <= 30 * DAY;
        case 'inactive':
          return !t || Date.now() - t > 30 * DAY;
        default:
          return true;
      }
    });
  }, [rows, search, filter]);

  const columns = [
    {
      title: 'שם לקוח',
      dataIndex: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name, 'he'),
      render: (v, r) => (
        <Space direction='vertical' size={0}>
          <Text strong>{v}</Text>
          {r.inSession && <Tag color='green'>בסשן עכשיו</Tag>}
        </Space>
      ),
    },
    {
      title: 'טלפון / אימייל',
      dataIndex: 'phone',
      render: (_, r) => (
        <Space direction='vertical' size={0}>
          {r.phone && <Text style={{ direction: 'ltr' }}>{r.phone}</Text>}
          {r.email && (
            <Text type='secondary' style={{ fontSize: 12 }}>
              {r.email}
            </Text>
          )}
        </Space>
      ),
    },
    {
      title: 'כניסה אחרונה',
      dataIndex: 'lastLogin',
      defaultSortOrder: 'descend',
      sorter: (a, b) => (a.lastLogin || 0) - (b.lastLogin || 0),
      render: v =>
        v ? (
          <Space direction='vertical' size={0}>
            <Text strong>{relativeLabel(v)}</Text>
            <Text type='secondary' style={{ fontSize: 12 }}>
              {dayjs(v).format('DD/MM/YYYY HH:mm')}
            </Text>
          </Space>
        ) : (
          <Text type='secondary'>—</Text>
        ),
    },
    {
      title: 'סטטוס',
      dataIndex: 'lastLogin',
      key: 'status',
      render: v => {
        const s = statusOf(v);
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: 'תאריך רישום',
      dataIndex: 'createdAt',
      sorter: (a, b) => (a.createdAt || 0) - (b.createdAt || 0),
      render: v => (v ? dayjs(v).format('DD/MM/YYYY') : '—'),
    },
    {
      title: 'יתרת זמן',
      dataIndex: 'remainingTime',
      sorter: (a, b) => a.remainingTime - b.remainingTime,
      render: v => formatTime(v),
    },
    {
      title: 'סה"כ כניסות',
      dataIndex: 'loginCount',
      sorter: (a, b) => a.loginCount - b.loginCount,
      render: v => v || '—',
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} md={6}>
          <StatCard title='נכנסו היום' value={stats.today} color='success' loading={loading} />
        </Col>
        <Col xs={12} md={6}>
          <StatCard title='נכנסו ב-7 ימים' value={stats.week} color='primary' loading={loading} />
        </Col>
        <Col xs={12} md={6}>
          <StatCard title='לא פעילים (30+ יום)' value={stats.inactive} color='error' loading={loading} />
        </Col>
        <Col xs={12} md={6}>
          <StatCard title='סה"כ לקוחות' value={stats.total} color='info' loading={loading} />
        </Col>
      </Row>

      <Card>
        <Space wrap style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder='חיפוש לפי שם, טלפון או אימייל'
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ width: 280 }}
          />
          <Segmented options={FILTERS} value={filter} onChange={setFilter} />
          <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
            רענן
          </Button>
        </Space>
        <Table
          columns={columns}
          dataSource={filtered}
          loading={loading}
          pagination={{ pageSize: 25, showSizeChanger: true, showTotal: t => `${t} לקוחות` }}
          scroll={{ x: 'max-content' }}
          locale={{ emptyText: <Empty description='אין לקוחות להצגה' /> }}
        />
      </Card>
    </div>
  );
};

export default ActivityPage;
