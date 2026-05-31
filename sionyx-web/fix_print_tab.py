content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

# Step 1: Add printLogs state after sessionSearch state
old1 = "  const [activeTab, setActiveTab] = useState('revenue');"
new1 = """  const [activeTab, setActiveTab] = useState('revenue');
  const [printLogs, setPrintLogs] = useState([]);
  const [printLogsLoading, setPrintLogsLoading] = useState(false);
  const [printSearch, setPrintSearch] = useState('');"""
c1 = content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

# Step 2: Add printLogs realtime listener after sessions useEffect
old2 = "  }, [activeTab, orgId]);"
new2 = """  }, [activeTab, orgId]);

  useEffect(() => {
    if (activeTab !== 'prints' || !orgId) return;
    setPrintLogsLoading(true);
    const logsRef = ref(database, `organizations/${orgId}/printLogs`);
    const unsub = onValue(logsRef, (snap) => {
      if (snap.exists()) {
        const data = snap.val();
        const logs = [];
        Object.entries(data).forEach(([userId, userLogs]) => {
          Object.entries(userLogs).forEach(([logKey, log]) => {
            logs.push({ id: logKey, ...log, userId });
          });
        });
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        setPrintLogs(logs);
      } else {
        setPrintLogs([]);
      }
      setPrintLogsLoading(false);
    }, (err) => {
      logger.error('Failed to load print logs:', err);
      setPrintLogsLoading(false);
    });
    return () => off(logsRef, 'value', unsub);
  }, [activeTab, orgId]);"""
c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND"); exit()

# Step 3: Add prints tab to Tabs items
old3 = "        { key: 'sessions', label: <span><HistoryOutlined /> היסטוריית שימוש</span> },\n      ]} />"
new3 = """        { key: 'sessions', label: <span><HistoryOutlined /> היסטוריית שימוש</span> },
        { key: 'prints', label: <span><PrinterOutlined /> היסטוריית הדפסות</span> },
      ]} />"""
c3 = content.count(old3)
print(f"Step 3: {c3}")
if c3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND"); exit()

# Step 4: Add prints tab content before closing motion.div
old4 = "    </motion.div>\n  );\n};\n\nexport default ReportsPage;"
new4 = """      {activeTab === 'prints' && (
        <Space direction='vertical' size={24} style={{ width: '100%', marginTop: 24 }}>
          <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <Title level={2} style={{ marginBottom: 8, fontWeight: 700, color: '#1f2937' }}>היסטוריית הדפסות</Title>
              <Text style={{ color: '#6b7280', fontSize: 15 }}>תיעוד כל עבודות ההדפסה</Text>
            </div>
            <Input.Search
              placeholder="חפש לפי מסמך, משתמש או מדפסת..."
              value={printSearch}
              onChange={e => setPrintSearch(e.target.value)}
              style={{ width: 300 }}
              allowClear
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <Card
              title={<Space><PrinterOutlined style={{ color: '#667eea' }} /><span>הדפסות</span>{printLogs.length > 0 && <Tag color='blue'>{printLogs.length}</Tag>}</Space>}
              bordered={false}
              style={{ borderRadius: 16 }}
            >
              <Table
                dataSource={printLogs.filter(l => {
                  if (!printSearch) return true;
                  return (l.docName || '').toLowerCase().includes(printSearch.toLowerCase()) ||
                         (l.userId || '').toLowerCase().includes(printSearch.toLowerCase()) ||
                         (l.printerName || '').toLowerCase().includes(printSearch.toLowerCase());
                })}
                columns={[
                  { title: 'תאריך', dataIndex: 'timestamp', key: 'timestamp', render: v => v ? dayjs(v).format('DD/MM/YYYY HH:mm') : '-', sorter: (a,b) => new Date(a.timestamp)-new Date(b.timestamp), defaultSortOrder: 'descend' },
                  { title: 'מסמך', dataIndex: 'docName', key: 'docName', render: v => v || '-', ellipsis: true },
                  { title: 'משתמש', dataIndex: 'userId', key: 'userId', render: v => v ? v.substring(0,12)+'...' : '-', ellipsis: true },
                  { title: 'מחשב', dataIndex: 'computerName', key: 'computerName', render: v => v || '-' },
                  { title: 'מדפסת', dataIndex: 'printerName', key: 'printerName', render: v => v || '-', ellipsis: true },
                  { title: 'עמודים', dataIndex: 'pages', key: 'pages', render: v => v || 0, sorter: (a,b) => (a.pages||0)-(b.pages||0) },
                  { title: 'עלות', dataIndex: 'cost', key: 'cost', render: v => v != null ? parseFloat(v).toFixed(2) + ' \u20aa' : '-', sorter: (a,b) => (a.cost||0)-(b.cost||0) },
                  { title: 'יתרה אחרי', dataIndex: 'remaining', key: 'remaining', render: v => v != null ? parseFloat(v).toFixed(2) + ' \u20aa' : '-' },
                ]}
                rowKey='id'
                loading={printLogsLoading}
                pagination={{ pageSize: 20, showSizeChanger: true, showTotal: total => 'סה"כ ' + total + ' הדפסות' }}
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
c4 = content.count(old4)
print(f"Step 4: {c4}")
if c4 == 1:
    content = content.replace(old4, new4, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 4: OK - file written")
else:
    print("Step 4: NOT FOUND")
