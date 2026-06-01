f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '    "organizations": {\n      ".read": "auth != null",\n      ".write": false,'
new = '    "organizations": {\n      ".read": "auth != null",\n      ".write": false,\n      "$orgId": {\n        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        }\n      },'

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'database.rules.json', 'w', encoding='utf-8').write(c)
print("OK")
