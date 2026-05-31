new_content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

# Step 1: Add Tabs to antd imports
old1 = "  Statistic,\n} from 'antd';"
new1 = "  Statistic,\n  Tabs,\n  Input,\n  Select,\n} from 'antd';"
c1 = new_content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    new_content = new_content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

# Step 2: Add HistoryOutlined to antd icons
old2 = "  CrownOutlined,\n} from '@ant-design/icons';"
new2 = "  CrownOutlined,\n  HistoryOutlined,\n  UserOutlined,\n  LaptopOutlined,\n  ClockCircleOutlined,\n} from '@ant-design/icons';"
c2 = new_content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    new_content = new_content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND"); exit()

# Step 3: Add firebase import after useOrgId import
old3 = "import { useOrgId } from '../hooks/useOrgId';"
new3 = "import { useOrgId } from '../hooks/useOrgId';\nimport { ref, get } from 'firebase/database';\nimport { database } from '../config/firebase';"
c3 = new_content.count(old3)
print(f"Step 3: {c3}")
if c3 == 1:
    new_content = new_content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND"); exit()

# Step 4: Add sessionLogs state and load function after orgId
old4 = "  const orgId = useOrgId();\n  const dateRange = useMemo"
new4 = """  const orgId = useOrgId();
  const [sessionLogs, setSessionLogs] = useState([]);
  const [sessionLogsLoading, setSessionLogsLoading] = useState(false);
  const [sessionSearch, setSessionSearch] = useState('');
  const [activeTab, setActiveTab] = useState('revenue');

  const loadSessionLogs = useCallback(async () => {
    if (!orgId) return;
    setSessionLogsLoading(true);
    try {
      const snap = await get(ref(database, `organizations/${orgId}/sessionLogs`));
      if (snap.exists()) {
        const data = snap.val();
        const logs = [];
        Object.entries(data).forEach(([userId, userLogs]) => {
          Object.entries(userLogs).forEach(([logKey, log]) => {
            logs.push({ id: logKey, ...log, userId });
          });
        });
        logs.sort((a, b) => new Date(b.endTime) - new Date(a.endTime));
        setSessionLogs(logs);
      }
    } catch (err) {
      logger.error('Failed to load session logs:', err);
    }
    setSessionLogsLoading(false);
  }, [orgId]);

  useEffect(() => {
    if (activeTab === 'sessions') loadSessionLogs();
  }, [activeTab, loadSessionLogs]);

  const dateRange = useMemo"""
c4 = new_content.count(old4)
print(f"Step 4: {c4}")
if c4 == 1:
    new_content = new_content.replace(old4, new4, 1)
    print("Step 4: OK")
else:
    print("Step 4: NOT FOUND"); exit()

# Step 5: Replace the return content to wrap in Tabs
old5 = "  return (\n    <motion.div style={{ direction: 'rtl' }} variants={containerVariants} initial='hidden' animate='visible'>"
new5 = """  const sessionColumns = [
    {
      title: 'תאריך סיום',
      dataIndex: 'endTime',
      key: 'endTime',
      render: v => v ? dayjs(v).format('DD/MM/YYYY HH:mm') : '-',
      sorter: (a, b) => new Date(a.endTime) - new Date(b.endTime),
      defaultSortOrder: 'descend',
    },
    {
      title: 'משתמש',
      dataIndex: 'userId',
      key: 'userId',
      render: v => v ? v.substring(0, 12) + '...' : '-',
      ellipsis: true,
    },
    {
      title: 'מחשב',
      dataIndex: 'computerName',
      key: 'computerName',
      render: v => v || '-',
    },
    {
      title: 'זמן שימוש',
      dataIndex: 'usedSeconds',
      key: 'usedSeconds',
      render: v => {
        if (!v) return '-';
        const m = Math.floor(v / 60);
        const s = v % 60;
        return `${m}:${String(s).padStart(2, '0')} דק'`;
      },
      sorter: (a, b) => (a.usedSeconds || 0) - (b.usedSeconds || 0),
    },
    {
      title: 'דקות שנותרו',
      dataIndex: 'remainingSeconds',
      key: 'remainingSeconds',
      render: v => v != null ? `${Math.floor(v / 60)} דק'` : '-',
    },
    {
      title: 'סיבת סיום',
      dataIndex: 'reason',
      key: 'reason',
      render: v => {
        const map = { user: 'יציאה רגילה', expired: 'נגמר זמן', idle: 'חוסר פעילות', hours: 'שעות פעילות', hours_force: 'כיבוי כפוי' };
        return <Tag color={v === 'user' ? 'green' : v === 'expired' ? 'orange' : 'red'}>{map[v] || v}</Tag>;
      },
    },
  ];

  const filteredSessionLogs = sessionLogs.filter(log => {
    if (!sessionSearch) return true;
    return (log.userId || '').toLowerCase().includes(sessionSearch.toLowerCase()) ||
           (log.computerName || '').toLowerCase().includes(sessionSearch.toLowerCase());
  });

  return (
    <motion.div style={{ direction: 'rtl' }} variants={containerVariants} initial='hidden' animate='visible'>
      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginBottom: 0 }} items={[
        { key: 'revenue', label: <span><DollarOutlined /> דוח הכנסות</span> },
        { key: 'sessions', label: <span><HistoryOutlined /> היסטוריית שימוש</span> },
      ]} />"""
c5 = new_content.count(old5)
print(f"Step 5: {c5}")
if c5 == 1:
    new_content = new_content.replace(old5, new5, 1)
    print("Step 5: OK")
else:
    print("Step 5: NOT FOUND"); exit()

# Step 6: Add sessions tab content before closing motion.div
old6 = "    </motion.div>\n  );\n};\n\nexport default ReportsPage;"
new6 = """      {activeTab === 'sessions' && (
        <Space direction='vertical' size={24} style={{ width: '100%', marginTop: 24 }}>
          <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <Title level={2} style={{ marginBottom: 8, fontWeight: 700, color: '#1f2937' }}>היסטוריית שימוש</Title>
              <Text style={{ color: '#6b7280', fontSize: 15 }}>תיעוד כל הסשנים של המשתמשים</Text>
            </div>
            <Input.Search
              placeholder="חפש לפי משתמש או מחשב..."
              value={sessionSearch}
              onChange={e => setSessionSearch(e.target.value)}
              style={{ width: 280 }}
              allowClear
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <Card
              title={<Space><HistoryOutlined style={{ color: '#667eea' }} /><span>סשנים</span>{filteredSessionLogs.length > 0 && <Tag color='blue'>{filteredSessionLogs.length}</Tag>}</Space>}
              bordered={false}
              style={{ borderRadius: 16 }}
              extra={<Button icon={<ReloadOutlined />} onClick={loadSessionLogs} loading={sessionLogsLoading}>רענן</Button>}
            >
              <Table
                dataSource={filteredSessionLogs}
                columns={sessionColumns}
                rowKey='id'
                loading={sessionLogsLoading}
                pagination={{ pageSize: 20, showSizeChanger: true, showTotal: total => `סה"כ ${total} סשנים` }}
                size='middle'
                locale={{ emptyText: <Empty description='אין נתונים עדיין' image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
              />
            </Card>
          </motion.div>
        </Space>
      )}
    </motion.div>
  );
};

export default ReportsPage;"""
c6 = new_content.count(old6)
print(f"Step 6: {c6}")
if c6 == 1:
    new_content = new_content.replace(old6, new6, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(new_content)
    print("Step 6: OK - file written")
else:
    print("Step 6: NOT FOUND"); exit()
