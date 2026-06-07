content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\components\MainLayout.jsx', encoding='utf-8').read()
old = '''  const handleLogout = async () => {
    await signOut();
    logout();
    navigate('/admin/login');
  };'''
new = '''  const handleLogout = async () => {
    await signOut();
    logout();
    localStorage.removeItem('admin-auth-storage');
    localStorage.removeItem('adminOrgId');
    navigate('/login');
  };'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\components\MainLayout.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
