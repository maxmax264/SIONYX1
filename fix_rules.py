content = open(r'database.rules.json', encoding='utf-8').read()
old = '''      "$uid": {
        ".read": "auth.uid === $uid",
        ".write": false,'''
new = '''      "$uid": {
        ".read": "auth.uid === $uid",
        ".write": false,
        "displayName": {
          ".read": "auth != null",
          ".write": "auth.uid === $uid"
        },'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'database.rules.json', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
