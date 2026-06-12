content = open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', encoding='utf-8').read()

old = '"$messageId": {\n            ".read": "auth != null && (data.child(\'toUserId\').val() == auth.uid || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'isAdmin\').val() === true || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'role\').val() === \'admin\' || root.child(\'supervisors\').child(auth.uid).child(\'organizations\').child($orgId).exists())",\n            ".write": "auth != null && ((!data.exists() && (root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'isAdmin\').val() === true || root.child(\'organizations\').child($orgId).child(\'users\').child(auth.uid).child(\'role\').val() === \'admin\' || root.child(\'supervisors\').child(auth.uid).child(\'organizations\').child($orgId).exists())) || data.child(\'toUserId\').val() == auth.uid)",'

idx = content.find('"$messageId"')
print(repr(content[idx:idx+600]))
