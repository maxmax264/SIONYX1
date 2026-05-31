content = open(r'.\src\App.jsx', encoding='utf-8').read()

old = """  const { setAuth, setAdmin, setLoading } = useAuthStore();
  const { setSupervisorAuth, setSupervisor, setSupervisorLoading } = useSupervisorAuthStore();"""

new = """  const { setUser, setLoading } = useAuthStore();
  const { setSupervisor, setLoading: setSupervisorLoading } = useSupervisorAuthStore();"""

count = content.count(old)
print(f"Step 1: {count} matches")
if count != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old, new, 1)

old2 = """      setAuth(user);
      if (user) {
        try {
          const adminData = await getCurrentAdminData(user.uid);
          setAdmin(adminData);"""

new2 = """      setUser(user);
      if (user) {
        try {
          const adminData = await getCurrentAdminData(user.uid);
          setUser(adminData);"""

count2 = content.count(old2)
print(f"Step 2: {count2} matches")
if count2 != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old2, new2, 1)

old3 = """      setSupervisorAuth(user);"""
new3 = """      setSupervisor(user ? { uid: user.uid } : null);"""

count3 = content.count(old3)
print(f"Step 3: {count3} matches")
if count3 != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old3, new3, 1)

old4 = """  }, [setAuth, setAdmin, setLoading, setSupervisorAuth, setSupervisor, setSupervisorLoading]);"""
new4 = """  }, [setUser, setLoading, setSupervisor, setSupervisorLoading]);"""

count4 = content.count(old4)
print(f"Step 4: {count4} matches")
if count4 != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old4, new4, 1)

open(r'.\src\App.jsx', 'w', encoding='utf-8').write(content)
print("OK - file written")
