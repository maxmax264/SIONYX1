f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()

old = '    "supervisors": {\n      "$uid": {'
new = '    "supervisors": {\n      ".read": "auth != null",\n      "$uid": {'

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'database.rules.json', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
