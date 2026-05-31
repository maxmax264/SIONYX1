content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

old = "      if (!showOperatorTopups && p.type === 'admin_charge') return false;"
new = "      if (!showOperatorTopups && (p.type === 'admin_charge' || p.note === 'טעינת מפעיל')) return false;"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
