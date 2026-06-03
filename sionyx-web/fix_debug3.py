f = open(r'.\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()

old = "if (snap.exists()) { const val = snap.val(); const filtered = Object.fromEntries(Object.entries(val).filter(([k,v]) => v !== '')); setDesign({ ...DEFAULTS, ...filtered }); }"
new = "if (snap.exists()) { const val = snap.val(); console.log('RAW:', JSON.stringify(val)); const filtered = Object.fromEntries(Object.entries(val).filter(([k,v]) => v !== '' && v !== null && v !== undefined)); console.log('FILTERED:', JSON.stringify(filtered)); setDesign({ ...DEFAULTS, ...filtered }); }"

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
