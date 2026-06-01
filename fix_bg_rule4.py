f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '"$orgId": {\n        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        }\n      },\n      \n      "$orgId": {\n        "users": {'
new = '"$orgId": {\n        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        },\n        "users": {'

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'database.rules.json', 'w', encoding='utf-8').write(c)
print("OK")
