content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "{ key: 'purchases', label: 'רכישות' },\n            { key: 'sessions', label: '\u00a0\u00a0שימוש (' + userSessions.length + ')' },\n            { key: 'prints', label: '\u00a0\u00a0הדפסות (' + userPrints.length + ')' },"
new = "{ key: 'purchases', label: 'רכישות' },\n            { key: 'sessions', label: 'שימוש (' + userSessions.length + ')' },\n            { key: 'prints', label: 'הדפסות (' + userPrints.length + ')' },"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)

# Add tabBarGutter
old2 = "activeKey={userHistoryTab} onChange={setUserHistoryTab}"
new2 = "activeKey={userHistoryTab} onChange={setUserHistoryTab} tabBarGutter={32}"

count2 = content.count(old2)
print(f"Found2 {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
