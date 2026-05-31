content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

old = "      render: v => v === 'admin_charge' ? <Tag color='blue'>טעינת מפעיל</Tag> : <Tag color='green'>רכישה</Tag>,"
new = "      render: (v, record) => (v === 'admin_charge' || record.note === 'טעינת מפעיל') ? <Tag color='blue'>טעינת מפעיל</Tag> : <Tag color='green'>רכישה</Tag>,"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
