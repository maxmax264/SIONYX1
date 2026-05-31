content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "style={{ marginTop: 16 }} items={["
new = "style={{ marginTop: 24, marginBottom: 16 }} items={["

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
