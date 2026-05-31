content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "usedSeconds', render: v => v ? Math.floor(v/60) + \" דק'\" : '-' }"
new = "usedSeconds', render: v => v ? (v < 60 ? v + \" שנ'\" : Math.floor(v/60) + \" דק'\") : '-' }"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
