content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

old = "  const orgId = useOrgId();\n\n  const dateRange = useMemo"
new = """  const orgId = useOrgId();
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

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
