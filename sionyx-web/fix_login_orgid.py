content = open(r'.\src\pages\LoginPage.jsx', encoding='utf-8').read()

old = "result.success) {\n      setUser(result.user);\n      setFailedAttempts(0);"
new = "result.success) {\n      setUser(result.user);\n      setFailedAttempts(0);\n      localStorage.setItem('adminOrgId', values.orgId);"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\LoginPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
