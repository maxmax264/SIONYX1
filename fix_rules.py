f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '''    "sessionLogs": {
      "$userId": {
        ".read": "auth.uid === $userId || root.child('organizations/sionov/users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations/sionov/users').child(auth.uid).child('role').val() === 'admin'",'''

new = '''    "systemSettings": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "sessionLogs": {
      "$userId": {
        ".read": "auth.uid === $userId || root.child('organizations/sionov/users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations/sionov/users').child(auth.uid).child('role').val() === 'admin'",'''

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'database.rules.json', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
