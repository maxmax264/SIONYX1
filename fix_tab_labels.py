content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "{ key: 'purchases', label: 'רכישות' },\n            { key: 'sessions', label: 'שימוש (' + userSessions.length + ')' },\n            { key: 'prints', label: 'הדפסות (' + userPrints.length + ')' },"
new = "{ key: 'purchases', label: 'רכישות' },\n            { key: 'sessions', label: ' שימוש (' + userSessions.length + ')' },\n            { key: 'prints', label: ' הדפסות (' + userPrints.length + ')' },"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND - checking")
    idx = content.find("key: 'purchases'")
    print(repr(content[idx:idx+200]))
