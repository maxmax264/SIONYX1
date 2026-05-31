content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

# Step 1: Add firebase imports
old1 = "import { useOrgId } from '../hooks/useOrgId';"
new1 = "import { useOrgId } from '../hooks/useOrgId';\nimport { ref, onValue, off } from 'firebase/database';\nimport { database } from '../config/firebase';"
c1 = content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

# Step 2: Add Tabs to antd imports - find existing antd import
old2 = "  Form,\n} from 'antd';"
new2 = "  Form,\n  Tabs,\n} from 'antd';"
c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND - trying alternative")
    old2b = "  Tag,\n} from 'antd';"
    new2b = "  Tag,\n  Tabs,\n} from 'antd';"
    c2b = content.count(old2b)
    print(f"Step 2b: {c2b}")
    if c2b == 1:
        content = content.replace(old2b, new2b, 1)
        print("Step 2b: OK")
    else:
        print("Step 2b: NOT FOUND - checking antd imports")
        idx = content.find("from 'antd'")
        print(repr(content[idx-200:idx+10]))
        exit()

# Step 3: Add state for user history
old3 = "  const [kicking, setKicking] = useState(false);"
new3 = """  const [kicking, setKicking] = useState(false);
  const [userSessions, setUserSessions] = useState([]);
  const [userPrints, setUserPrints] = useState([]);
  const [userHistoryTab, setUserHistoryTab] = useState('purchases');"""
c3 = content.count(old3)
print(f"Step 3: {c3}")
if c3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND"); exit()

# Step 4: Load user history when drawer opens
old4 = "    setLoadingPurchases(true);\n    setLoadingMessages(true);"
new4 = """    setLoadingPurchases(true);
    setLoadingMessages(true);
    setUserSessions([]);
    setUserPrints([]);
    setUserHistoryTab('purchases');"""
c4 = content.count(old4)
print(f"Step 4: {c4}")
if c4 == 1:
    content = content.replace(old4, new4, 1)
    print("Step 4: OK")
else:
    print("Step 4: NOT FOUND"); exit()

# Step 5: Add useEffect for realtime session/print logs when drawer opens
old5 = "  const handleViewUser = async record => {"
new5 = """  useEffect(() => {
    if (!drawerVisible || !selectedUser || !orgId) return;
    const sessRef = ref(database, `organizations/${orgId}/sessionLogs/${selectedUser.uid}`);
    const printRef = ref(database, `organizations/${orgId}/printLogs/${selectedUser.uid}`);
    const unsubSess = onValue(sessRef, snap => {
      if (snap.exists()) {
        const logs = Object.entries(snap.val()).map(([k, v]) => ({ id: k, ...v }));
        logs.sort((a, b) => new Date(b.endTime) - new Date(a.endTime));
        setUserSessions(logs);
      } else setUserSessions([]);
    });
    const unsubPrint = onValue(printRef, snap => {
      if (snap.exists()) {
        const logs = Object.entries(snap.val()).map(([k, v]) => ({ id: k, ...v }));
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        setUserPrints(logs);
      } else setUserPrints([]);
    });
    return () => { off(sessRef, 'value', unsubSess); off(printRef, 'value', unsubPrint); };
  }, [drawerVisible, selectedUser, orgId]);

  const handleViewUser = async record => {"""
c5 = content.count(old5)
print(f"Step 5: {c5}")
if c5 == 1:
    content = content.replace(old5, new5, 1)
    print("Step 5: OK")
else:
    print("Step 5: NOT FOUND"); exit()

# Step 6: Wrap drawer content in Tabs
old6 = "      </Drawer>"
new6 = """        {selectedUser && (
          <Tabs activeKey={userHistoryTab} onChange={setUserHistoryTab} style={{ marginTop: 8 }} items={[
            { key: 'purchases', label: 'רכישות' },
            { key: 'sessions', label: 'שימוש (' + userSessions.length + ')' },
            { key: 'prints', label: 'הדפסות (' + userPrints.length + ')' },
          ]} />
        )}
        {userHistoryTab === 'sessions' && selectedUser && (
          <Table
            dataSource={userSessions}
            rowKey='id'
            size='small'
            style={{ marginTop: 8 }}
            pagination={{ pageSize: 10 }}
            locale={{ emptyText: 'אין נתונים עדיין' }}
            columns={[
              { title: 'תאריך', dataIndex: 'endTime', render: v => v ? new Date(v).toLocaleString('he-IL') : '-', defaultSortOrder: 'descend', sorter: (a,b) => new Date(a.endTime)-new Date(b.endTime) },
              { title: 'מחשב', dataIndex: 'computerName', render: v => v || '-' },
              { title: 'זמן שימוש', dataIndex: 'usedSeconds', render: v => v ? Math.floor(v/60) + " דק'" : '-' },
              { title: 'סיבת סיום', dataIndex: 'reason', render: v => { const map = { user: 'יציאה', expired: 'נגמר זמן', idle: 'חוסר פעילות' }; return map[v] || v || '-'; } },
            ]}
          />
        )}
        {userHistoryTab === 'prints' && selectedUser && (
          <Table
            dataSource={userPrints}
            rowKey='id'
            size='small'
            style={{ marginTop: 8 }}
            pagination={{ pageSize: 10 }}
            locale={{ emptyText: 'אין נתונים עדיין' }}
            columns={[
              { title: 'תאריך', dataIndex: 'timestamp', render: v => v ? new Date(v).toLocaleString('he-IL') : '-', defaultSortOrder: 'descend', sorter: (a,b) => new Date(a.timestamp)-new Date(b.timestamp) },
              { title: 'מסמך', dataIndex: 'docName', render: v => v || '-', ellipsis: true },
              { title: 'עמודים', dataIndex: 'pages', render: v => v || 0 },
              { title: 'עלות', dataIndex: 'cost', render: v => v != null ? parseFloat(v).toFixed(2) + ' \u20aa' : '-' },
            ]}
          />
        )}
      </Drawer>"""
c6 = content.count(old6)
print(f"Step 6: {c6}")
if c6 == 1:
    content = content.replace(old6, new6, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 6: OK - file written")
else:
    print(f"Step 6: found {c6} matches - NOT SAFE")
