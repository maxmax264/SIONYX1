content = open(r'.\database.rules.json', encoding='utf-8').read()

old = '''          "kioskBackgroundEnabled": { ".read": true },
          "kioskBackgroundUrl": { ".read": true },
          "kioskRefreshAt": { ".read": true },'''

new = '''          "kioskBackgroundEnabled": { ".read": true },
          "kioskBackgroundUrl": { ".read": true },
          "kioskRefreshAt": { ".read": true },
          "authDesign": { ".read": true },
          "kioskDesign": { ".read": true },'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\database.rules.json', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
