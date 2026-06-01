f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

# מחק את metadata שהוספנו
old = '        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true }\n        },\n        "users": {'
new = '        "users": {'
assert c.count(old) == 1
c = c.replace(old, new, 1)

# הוסף read ציבורי ל-metadata הקיים
old2 = '        "metadata": {\n          ".read": "auth != null &&'
new2 = '        "metadata": {\n          "kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true },\n          ".read": "auth != null &&'
assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

open(r'database.rules.json', 'w', encoding='utf-8').write(c)
print("OK")
