content = open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', encoding='utf-8').read()

old = '''            onChange={(_, hex) => handleChange("overlayColor1", hex)} />'''
new = '''            onChange={(color) => handleChange("overlayColor1", color.toHexString())} />'''

count = content.count(old)
print(f"color1: {count}")
if count == 1:
    content = content.replace(old, new, 1)

old2 = '''            onChange={(_, hex) => handleChange("overlayColor2", hex)} />'''
new2 = '''            onChange={(color) => handleChange("overlayColor2", color.toHexString())} />'''

count2 = content.count(old2)
print(f"color2: {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)

if count == 1 and count2 == 1:
    open(r'.\sionyx-web\src\components\settings\AuthDesignSettings.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
