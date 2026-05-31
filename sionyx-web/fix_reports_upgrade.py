content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

# Step 1: Add users import
old1 = "import { getOrganizationStats } from '../services/organizationService';"
new1 = "import { getOrganizationStats } from '../services/organizationService';\nimport { getAllUsers } from '../services/userService';"
c1 = content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

# Step 2: Add users state and showOperator state
old2 = "  const [activeTab, setActiveTab] = useState('revenue');"
new2 = """  const [activeTab, setActiveTab] = useState('revenue');
  const [usersMap, setUsersMap] = useState({});
  const [showOperatorTopups, setShowOperatorTopups] = useState(false);"""
c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND"); exit()

# Step 3: Add users loading in loadData
old3 = "    try {\n      const result = await getOrganizationStats(orgId);\n      if (result.success && result.stats?.purchases) {\n        setAllPurchases(result.stats.purchases);\n      }\n    } catch (err) {\n      logger.error('Failed to load reports data:', err);\n    }\n    setLoading(false);"
new3 = """    try {
      const [statsResult, usersResult] = await Promise.all([
        getOrganizationStats(orgId),
        getAllUsers(orgId),
      ]);
      if (statsResult.success && statsResult.stats?.purchases) {
        setAllPurchases(statsResult.stats.purchases);
      }
      if (usersResult.success && usersResult.users) {
        const map = {};
        usersResult.users.forEach(u => {
          map[u.uid] = `${u.firstName || ''} ${u.lastName || ''}`.trim() || u.phoneNumber || u.uid;
        });
        setUsersMap(map);
      }
    } catch (err) {
      logger.error('Failed to load reports data:', err);
    }
    setLoading(false);"""
c3 = content.count(old3)
print(f"Step 3: {c3}")
if c3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND"); exit()

# Step 4: Add showOperatorTopups filter to filteredPurchases
old4 = "    return allPurchases.filter(p => {\n      if (p.status !== 'completed') return false;"
new4 = """    return allPurchases.filter(p => {
      if (p.status !== 'completed') return false;
      if (!showOperatorTopups && p.type === 'admin_charge') return false;"""
c4 = content.count(old4)
print(f"Step 4: {c4}")
if c4 == 1:
    content = content.replace(old4, new4, 1)
    print("Step 4: OK")
else:
    print("Step 4: NOT FOUND"); exit()

# Step 5: Fix filteredPurchases useMemo deps
old5 = "  }, [allPurchases, dateRange]);"
new5 = "  }, [allPurchases, dateRange, showOperatorTopups]);"
c5 = content.count(old5)
print(f"Step 5: {c5}")
if c5 == 1:
    content = content.replace(old5, new5, 1)
    print("Step 5: OK")
else:
    print("Step 5: NOT FOUND"); exit()

# Step 6: Add user name column to purchases table
old6 = "    {\n      title: 'תאריך',\n      dataIndex: 'createdAt',\n      key: 'createdAt',\n      render: v => dayjs(v).format('DD/MM/YYYY HH:mm'),"
new6 = """    {
      title: 'משתמש',
      dataIndex: 'userId',
      key: 'userId',
      render: v => usersMap[v] || v || '—',
    },
    {
      title: 'סוג',
      dataIndex: 'type',
      key: 'type',
      render: v => v === 'admin_charge' ? <Tag color='blue'>טעינת מפעיל</Tag> : <Tag color='green'>רכישה</Tag>,
    },
    {
      title: 'תאריך',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: v => dayjs(v).format('DD/MM/YYYY HH:mm'),"""
c6 = content.count(old6)
print(f"Step 6: {c6}")
if c6 == 1:
    content = content.replace(old6, new6, 1)
    print("Step 6: OK")
else:
    print("Step 6: NOT FOUND"); exit()

# Step 7: Add checkbox to revenue tab header
old7 = "          <div>\n            <Title level={2} style={{ marginBottom: 8, fontWeight: 700, color: '#1f2937' }}>\n              דוחות הכנסות\n            </Title>\n            <Text style={{ color: '#6b7280', fontSize: 15 }}>\n              ניתוח הכנסות ורכישות לתקופה נבחרת\n            </Text>\n          </div>"
new7 = """          <div>
            <Title level={2} style={{ marginBottom: 8, fontWeight: 700, color: '#1f2937' }}>
              דוחות הכנסות
            </Title>
            <Text style={{ color: '#6b7280', fontSize: 15 }}>
              ניתוח הכנסות ורכישות לתקופה נבחרת
            </Text>
          </div>"""
c7 = content.count(old7)
print(f"Step 7: {c7} (skip if 0)")

# Step 7b: Add checkbox near export button
old7b = "            <Dropdown menu={{ items: exportMenuItems }} disabled={filteredPurchases.length === 0}>\n              <Button icon={<DownloadOutlined />}>ייצוא</Button>\n            </Dropdown>"
new7b = """            <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 13 }}>
              <input
                type='checkbox'
                checked={showOperatorTopups}
                onChange={e => setShowOperatorTopups(e.target.checked)}
              />
              הצג טעינות מפעיל
            </label>
            <Dropdown menu={{ items: exportMenuItems }} disabled={filteredPurchases.length === 0}>
              <Button icon={<DownloadOutlined />}>ייצוא</Button>
            </Dropdown>"""
c7b = content.count(old7b)
print(f"Step 7b: {c7b}")
if c7b == 1:
    content = content.replace(old7b, new7b, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 7b: OK - file written")
else:
    print("Step 7b: NOT FOUND")
