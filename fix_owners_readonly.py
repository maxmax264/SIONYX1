f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '    "owners": {\n      ".read": "auth != null",\n      ".write": "auth != null"\n    },'
new = '    "owners": {\n      ".read": "auth != null",\n      ".write": false\n    },'

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'database.rules.json', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
