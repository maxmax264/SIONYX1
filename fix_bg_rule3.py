f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '''      "$orgId": {
        "metadata": {
          "kioskBackgroundEnabled": { ".read": true },
          "kioskBackgroundUrl": { ".read": true }
        }
      },
      "$orgId": {
        "users": {'''
new = '''      "$orgId": {
        "metadata": {
          "kioskBackgroundEnabled": { ".read": true },
          "kioskBackgroundUrl": { ".read": true }
        },
        "users": {'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'database.rules.json', 'w', encoding='utf-8').write(c)
print("OK")
