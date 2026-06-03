f = open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()

old = '  const handleChange = (field, value) => {\n    save({ ...design, [field]: value });\n  };'
new = '  const handleChange = (field, value) => {\n    const updated = { ...design, [field]: value };\n    setDesign(updated);\n    save(updated);\n  };'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
