content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "        if (type === 'admin_charge') return <Tag color='blue'>טעינת מפעיל</Tag>;"
new = "        if (type === 'admin_charge' || record.note === 'טעינת מפעיל') return <Tag color='blue'>טעינת מפעיל</Tag>;"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
