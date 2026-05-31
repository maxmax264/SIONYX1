content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

# Step 1: Add firebase import
old1 = "import { useOrgId } from '../hooks/useOrgId';"
new1 = "import { useOrgId } from '../hooks/useOrgId';\nimport { ref, onValue, off } from 'firebase/database';\nimport { database } from '../config/firebase';"
c1 = content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

# Step 2: Replace loadSessionLogs with realtime version
old2 = """  const loadSessionLogs = useCallback(async () => {
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
  }, [activeTab, loadSessionLogs]);"""

new2 = """  const loadSessionLogs = useCallback(() => {}, []);

  useEffect(() => {
    if (activeTab !== 'sessions' || !orgId) return;
    setSessionLogsLoading(true);
    const logsRef = ref(database, `organizations/${orgId}/sessionLogs`);
    const unsub = onValue(logsRef, (snap) => {
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
      } else {
        setSessionLogs([]);
      }
      setSessionLogsLoading(false);
    }, (err) => {
      logger.error('Failed to load session logs:', err);
      setSessionLogsLoading(false);
    });
    return () => off(logsRef, 'value', unsub);
  }, [activeTab, orgId]);"""

c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 2: OK - file written")
else:
    print("Step 2: NOT FOUND")
