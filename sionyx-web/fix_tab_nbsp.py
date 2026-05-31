content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "{ key: 'sessions', label: ' \u05e9\u05d9\u05de\u05d5\u05e9 (' + userSessions.length + ')' },\n            { key: 'prints', label: ' \u05d4\u05d3\u05e4\u05e1\u05d5\u05ea (' + userPrints.length + ')' },"
new = "{ key: 'sessions', label: '\u00a0\u00a0\u05e9\u05d9\u05de\u05d5\u05e9 (' + userSessions.length + ')' },\n            { key: 'prints', label: '\u00a0\u00a0\u05d4\u05d3\u05e4\u05e1\u05d5\u05ea (' + userPrints.length + ')' },"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
