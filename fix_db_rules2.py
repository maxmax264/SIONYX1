content = open(r'.\database.rules.json', encoding='utf-8').read()

# Add sessionLogs and printLogs inside organizations/$orgId
old = '        "metadata": {'
new = '''        "sessionLogs": {
          "$userId": {
            ".read": "auth.uid === $userId || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'isAdmin\').val() === true || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'role\').val() === \'admin\'",
            ".write": "auth.uid === $userId"
          }
        },
        "printLogs": {
          "$userId": {
            ".read": "auth.uid === $userId || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'isAdmin\').val() === true || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'role\').val() === \'admin\'",
            ".write": "auth.uid === $userId"
          }
        },
        "metadata": {'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\database.rules.json', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
