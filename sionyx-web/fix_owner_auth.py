content = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8').read()

old = """  const load = async () => {
    setLoading(true);
    const [orgsRes, supRes] = await Promise.all([getAllOrgs(), getAllSupervisors()]);
    if (orgsRes.success) setOrgs(orgsRes.orgs);
    if (supRes.success) setSupervisors(supRes.supervisors);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);"""

new = """  const load = async () => {
    setLoading(true);
    const { getAuth } = await import("firebase/auth");
    const auth = getAuth();
    await new Promise(resolve => {
      if (auth.currentUser) return resolve();
      const unsub = auth.onAuthStateChanged(u => { unsub(); resolve(); });
    });
    const [orgsRes, supRes] = await Promise.all([getAllOrgs(), getAllSupervisors()]);
    if (orgsRes.success) setOrgs(orgsRes.orgs);
    if (supRes.success) setSupervisors(supRes.supervisors);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
