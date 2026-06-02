content = open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8').read()

old = '''        background: "#f5f5f5",'''
new = '''        background: "linear-gradient(135deg, #0F172A, #1E1B4B, #0F172A)",'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-web\src\components\settings\KioskDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
