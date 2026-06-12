content = open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', encoding='utf-8').read()

old = '        "metadata": {'
new = '''        "userReplies": {
          ".read": "auth != null && (root.child('organizations').child($orgId).child('users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations').child($orgId).child('users').child(auth.uid).child('role').val() === 'admin' || root.child('supervisors').child(auth.uid).child('organizations').child($orgId).exists())",
          "$replyId": {
            ".read": "auth != null",
            ".write": "auth != null && (data.child('fromUserId').val() == auth.uid || root.child('organizations').child($orgId).child('users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations').child($orgId).child('users').child(auth.uid).child('role').val() === 'admin' || root.child('supervisors').child(auth.uid).child('organizations').child($orgId).exists())"
          }
        },
        "metadata": {'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
