path = r'.\src\SionyxKiosk\Infrastructure\LocalDatabase.cs'
content = open(path, encoding='utf-8').read()

old = '        var path = dbPath ?? GetDefaultPath();\n        Directory.CreateDirectory(Path.GetDirectoryName(path)!);\n        _db = new LiteDatabase(path);\n        Logger.Debug("LocalDatabase opened at {Path}", path);'
new = '        var path = dbPath ?? GetDefaultPath();\n        Directory.CreateDirectory(Path.GetDirectoryName(path)!);\n        _db = new LiteDatabase(path);\n        try { Logger.Debug("LocalDatabase opened at {Path}", path); } catch { }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
