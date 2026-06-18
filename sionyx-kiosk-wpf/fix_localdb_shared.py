path = r'.\src\SionyxKiosk\Infrastructure\LocalDatabase.cs'
content = open(path, encoding='utf-8').read()

old = '        _db = new LiteDatabase(path);'
new = '        _db = new LiteDatabase(new ConnectionString(path) { Connection = ConnectionType.Shared });'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
