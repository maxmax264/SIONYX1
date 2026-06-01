f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

# בטל את השינוי הקודם
old = '    "organizations": {\n      ".read": "auth != null",\n      ".write": false,\n      "$orgId": {\n        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        }\n      },'
new = '    "organizations": {\n      ".read": "auth != null",\n      ".write": false,'
assert c.count(old) == 1
c = c.replace(old, new, 1)

# מצא את $orgId הקיים והוסף בתוכו
old2 = '      "$orgId": {\n        ".read": "auth != null && ('
new2 = '      "$orgId": {\n        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        },\n        ".read": "auth != null && ('
assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

open(r'database.rules.json', 'w', encoding='utf-8').write(c)
print("OK")
