import json

with open('current_rules.json', encoding='utf-16') as f:
    rules = json.load(f)

org_rules = rules['rules']['organizations']['$orgId']

org_rules['userReplies'] = {
    ".read": "auth != null && (root.child('organizations').child($orgId).child('users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations').child($orgId).child('users').child(auth.uid).child('role').val() === 'admin' || root.child('supervisors').child(auth.uid).child('organizations').child($orgId).exists())",
    "$replyId": {
        ".read": "auth != null && (data.child('fromUserId').val() == auth.uid || root.child('organizations').child($orgId).child('users').child(auth.uid).child('isAdmin').val() === true || root.child('organizations').child($orgId).child('users').child(auth.uid).child('role').val() === 'admin')",
        ".write": "auth != null && root.child('organizations').child($orgId).child('users').child(auth.uid).exists()",
        ".validate": "newData.hasChildren(['fromUserId', 'message', 'timestamp'])"
    }
}

with open('new_rules.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, indent=2, ensure_ascii=False)

print('Done')
